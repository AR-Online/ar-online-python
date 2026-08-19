"""O transporte do legado: dois endereços, duas credenciais, e o que não é o
gateway respondendo."""

from __future__ import annotations

import pytest

from aronline import (
    DEFAULT_BASE_URL,
    DEFAULT_LEGACY_BASE_URL,
    Client,
    LegacyApiError,
    LegacyArea,
)
from aronline.legacy.transport import LegacyTransport
from tests.support.fake_api import FakeApi


class TestOsDoisEnderecos:
    def test_a_area_de_legado_tem_endereco_proprio(self) -> None:
        assert DEFAULT_LEGACY_BASE_URL == "https://api.ar-online.com.br"
        assert DEFAULT_LEGACY_BASE_URL != DEFAULT_BASE_URL

    def test_monta_a_url_sobre_o_endereco_do_legado(self) -> None:
        transport = LegacyTransport(token="t", base_url="https://exemplo.dev/")

        url = transport.url("/gw/templates", {"type": "1", "vazio": None})

        assert url == "https://exemplo.dev/gw/templates?type=1"

    def test_usa_producao_quando_ninguem_diz_outro(self) -> None:
        url = LegacyTransport(token="t").url("/gw/templates")

        assert url == f"{DEFAULT_LEGACY_BASE_URL}/gw/templates"


class TestAsDuasCredenciais:
    def test_nenhuma_das_duas_vaza_para_a_area_da_outra(self, api: FakeApi) -> None:
        ambos = Client(
            base_url=api.base_url,
            token="tok-v3",
            legacy_base_url=api.base_url,
            legacy_token="tok-gw",
        )

        api.answers({"description": "ok"})
        ambos.legacy.status.voz("x")
        assert api.received.authorization == "tok-gw"

        api.answers({"data": []})
        ambos.templates.list()
        assert api.received.authorization == "Bearer tok-v3"

    def test_o_token_do_gateway_vai_cru_sem_bearer(self, api: FakeApi, legacy: LegacyArea) -> None:
        api.answers({"description": "ok"})

        legacy.status.voz("x")

        assert api.received.authorization == "tok-gw"
        assert "Bearer" not in (api.received.authorization or "")

    def test_sem_credencial_falha_antes_do_socket_dizendo_qual_falta(self, api: FakeApi) -> None:
        sem_token = Client(legacy_base_url=api.base_url)

        with pytest.raises(LegacyApiError) as caught:
            sem_token.legacy.status.email("x")

        assert caught.value.status == 401
        assert caught.value.http_status == 0
        assert "legacy_token" in caught.value.message
        assert caught.value.body is None


class TestNaoEhOGatewayRespondendo:
    def test_200_que_nao_e_json_vira_erro_do_sdk(self, api: FakeApi, legacy: LegacyArea) -> None:
        api.answers_raw(200, "<html>proxy</html>")

        with pytest.raises(LegacyApiError) as caught:
            legacy.status.email("x")

        assert "não é JSON" in caught.value.message
        assert caught.value.http_status == 200

    def test_502_de_html_falha_com_o_status_sem_erro_de_parser(
        self, api: FakeApi, legacy: LegacyArea
    ) -> None:
        api.answers_raw(502, "<html>bad gateway</html>")

        with pytest.raises(LegacyApiError) as caught:
            legacy.status.email("x")

        assert caught.value.status == 502
        assert caught.value.http_status == 502
        assert "502" in caught.value.message
        assert caught.value.body is None

    def test_endereco_inalcancavel_vira_o_mesmo_erro_com_status_zero(self) -> None:
        perdido = Client(legacy_base_url="http://127.0.0.1:1", legacy_token="tok-gw", timeout=2)

        with pytest.raises(LegacyApiError) as caught:
            perdido.legacy.status.email("x")

        assert caught.value.status == 0
        assert caught.value.http_status == 0


class TestORepr:
    def test_mostra_os_dois_codigos_que_importam(self) -> None:
        error = LegacyApiError(status=404, http_status=200, message="Template não encontrado")

        assert repr(error) == (
            "LegacyApiError(status=404, http_status=200, message='Template não encontrado')"
        )
