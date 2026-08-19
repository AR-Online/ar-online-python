"""O transporte: endereço, cabeçalho, envelope e recusa."""

from __future__ import annotations

import pytest

from aronline import DEFAULT_BASE_URL, ApiError
from aronline.http.transport import Transport
from tests.support.fake_api import FakeApi


@pytest.fixture
def transport(api: FakeApi) -> Transport:
    return Transport(token="tok", base_url=api.base_url)


@pytest.fixture
def anonymous_transport(api: FakeApi) -> Transport:
    """Sem token. Um construtor à parte, e não um parâmetro opcional: teste
    que quer provar o caminho SEM credencial não pode receber a do padrão."""
    return Transport(base_url=api.base_url)


class TestEndereco:
    def test_usa_producao_quando_ninguem_diz_outro(self) -> None:
        assert Transport().url("/v3/tags") == f"{DEFAULT_BASE_URL}/v3/tags"

    def test_nao_duplica_a_barra_quando_a_base_termina_em_uma(self) -> None:
        transport = Transport(base_url="https://exemplo.test///")

        assert transport.url("/v3/tags") == "https://exemplo.test/v3/tags"

    def test_poe_na_query_so_o_filtro_preenchido(self) -> None:
        transport = Transport(base_url="https://exemplo.test")
        url = transport.url("/v3/templates", {"channel": "sms", "outro": None})

        assert url == "https://exemplo.test/v3/templates?channel=sms"


class TestCabecalho:
    def test_monta_o_bearer_sozinho(self, api: FakeApi, transport: Transport) -> None:
        api.answers({"data": []})

        transport.envelope("/v3/tags")

        assert api.received.authorization == "Bearer tok"
        assert api.received.accept == "application/json"
        assert api.received.method == "GET"

    def test_nao_manda_credencial_em_rota_aberta(
        self, api: FakeApi, anonymous_transport: Transport
    ) -> None:
        api.answers({"version": "0.1.0"})

        anonymous_transport.bare("/v3/version", authenticated=False)

        assert api.received.authorization is None


class TestEnvelope:
    def test_devolve_o_que_esta_em_data(self, api: FakeApi, transport: Transport) -> None:
        api.answers({"data": [{"id": "a"}]})

        assert transport.envelope("/v3/tags") == [{"id": "a"}]

    def test_entrega_a_resposta_inteira_quando_a_rota_nao_envelopa(
        self, api: FakeApi, transport: Transport
    ) -> None:
        api.answers({"sources_tracked": 46})

        assert transport.bare("/v3/freshness") == {"sources_tracked": 46}

    def test_recusa_quando_a_rota_promete_data_e_nao_entrega(
        self, api: FakeApi, transport: Transport
    ) -> None:
        api.answers({"tags": []})

        with pytest.raises(ApiError) as caught:
            transport.envelope("/v3/tags")

        assert caught.value.code == "invalid_response"


class TestRecusa:
    def test_vira_api_error_com_tudo_do_corpo(self, api: FakeApi, transport: Transport) -> None:
        api.refuses(
            404,
            {
                "code": "not_found",
                "message": "Etiqueta não encontrada.",
                "request_id": "req-do-corpo",
            },
        )

        with pytest.raises(ApiError) as caught:
            transport.envelope("/v3/tags/1")

        error = caught.value
        assert error.status == 404
        assert error.code == "not_found"
        assert error.message == "Etiqueta não encontrada."
        assert error.request_id == "req-do-corpo"
        assert error.retryable is False

    def test_cai_no_request_id_do_cabecalho(self, api: FakeApi, transport: Transport) -> None:
        api.refuses(403, {"code": "forbidden", "message": "sem permissão"})

        with pytest.raises(ApiError) as caught:
            transport.envelope("/v3/tags")

        assert caught.value.request_id == "req-do-cabecalho"

    def test_le_o_retry_after_e_marca_repetivel(self, api: FakeApi, transport: Transport) -> None:
        api.refuses(
            429,
            {"code": "rate_limited", "message": "aguarde"},
            {"Retry-After": "30"},
        )

        with pytest.raises(ApiError) as caught:
            transport.envelope("/v3/tags")

        assert caught.value.retry_after_seconds == 30
        assert caught.value.retryable is True

    def test_ignora_retry_after_que_nao_e_numero(self, api: FakeApi, transport: Transport) -> None:
        api.refuses(
            503,
            {"code": "unavailable", "message": "volte depois"},
            {"Retry-After": "Wed, 21 Oct 2026 07:28:00 GMT"},
        )

        with pytest.raises(ApiError) as caught:
            transport.envelope("/v3/tags")

        assert caught.value.retry_after_seconds is None
        assert caught.value.retryable is True

    def test_carrega_field_e_details(self, api: FakeApi, transport: Transport) -> None:
        api.refuses(
            400,
            {
                "code": "invalid_value",
                "message": "channel aceita: email, sms, whatsapp, voice, letter.",
                "field": "channel",
                "details": [
                    {"field": "channel", "code": "invalid_value", "message": "fora da lista"}
                ],
            },
        )

        with pytest.raises(ApiError) as caught:
            transport.envelope("/v3/templates")

        assert caught.value.field == "channel"
        assert caught.value.details == [
            {"field": "channel", "code": "invalid_value", "message": "fora da lista"}
        ]

    def test_repr_mostra_o_que_o_suporte_pede(self) -> None:
        error = ApiError(status=404, code="not_found", message="sumiu", request_id="r-9")

        assert repr(error) == "ApiError(status=404, code='not_found', request_id='r-9')"


class TestNaoEhAApiRespondendo:
    def test_502_em_html_vira_api_error(self, api: FakeApi, transport: Transport) -> None:
        api.answers_raw(502, "<html>bad gateway</html>")

        with pytest.raises(ApiError) as caught:
            transport.envelope("/v3/tags")

        assert caught.value.status == 502
        assert caught.value.code == "invalid_response"

    def test_200_que_nao_e_json_tambem(self, api: FakeApi, transport: Transport) -> None:
        api.answers_raw(200, "nem json", "text/plain")

        with pytest.raises(ApiError) as caught:
            transport.bare("/v3/freshness")

        assert caught.value.code == "invalid_response"

    def test_endereco_fora_do_ar_vira_unreachable(self) -> None:
        offline = Transport(token="tok", base_url="http://127.0.0.1:1", timeout=2)

        with pytest.raises(ApiError) as caught:
            offline.bare("/v3/freshness")

        assert caught.value.status == 0
        assert caught.value.code == "unreachable"


class TestCredencialQueFalta:
    def test_rota_autenticada_sem_token_falha_antes_de_sair(
        self, anonymous_transport: Transport
    ) -> None:
        with pytest.raises(ApiError) as caught:
            anonymous_transport.envelope("/v3/tags")

        assert caught.value.status == 401
        assert caught.value.code == "unauthenticated"
        assert caught.value.request_id is None
