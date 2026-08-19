"""Modelos."""

from __future__ import annotations

import pytest

from aronline import ApiError, Client
from tests.support.fake_api import FakeApi

TEMPLATE = {
    "id": "9b2f-uuid",
    "name": "Aviso de boleto",
    "channel": "whatsapp",
    "subject": None,
    "body": "Olá {{1}}, seu boleto vence em {{2}}.",
    "active": True,
    "provider_identifier": "hx_boleto_01",
    "variables": [{"name": "1", "component": "body", "type": "text"}],
    "created_at": "2024-10-12T14:11:13-03:00",
    "updated_at": None,
}


class TestList:
    def test_devolve_os_modelos_desembrulhados(self, api: FakeApi, client: Client) -> None:
        api.answers({"data": [TEMPLATE]})

        assert client.templates.list() == [TEMPLATE]
        assert api.received.path == "/v3/templates"

    def test_leva_o_canal_como_filtro(self, api: FakeApi, client: Client) -> None:
        api.answers({"data": []})

        client.templates.list(channel="whatsapp")

        assert api.received.path == "/v3/templates?channel=whatsapp"

    def test_omite_o_filtro_quando_o_canal_nao_vem(self, api: FakeApi, client: Client) -> None:
        api.answers({"data": []})

        client.templates.list(channel=None)

        assert api.received.path == "/v3/templates"

    def test_lista_vazia_sem_inventar_nada(self, api: FakeApi, client: Client) -> None:
        api.answers({"data": []})

        assert client.templates.list() == []


class TestGet:
    def test_busca_pelo_uuid_publico(self, api: FakeApi, client: Client) -> None:
        api.answers({"data": TEMPLATE})

        assert client.templates.get("9b2f-uuid") == TEMPLATE
        assert api.received.path == "/v3/templates/9b2f-uuid"

    def test_escapa_o_id(self, api: FakeApi, client: Client) -> None:
        api.answers({"data": TEMPLATE})

        client.templates.get("../../ops/health")

        assert api.received.path == "/v3/templates/..%2F..%2Fops%2Fhealth"

    def test_modelo_que_nao_existe_ou_nao_e_seu_chega_como_404(
        self, api: FakeApi, client: Client
    ) -> None:
        api.refuses(404, {"code": "not_found", "message": "Modelo não encontrado."})

        with pytest.raises(ApiError) as caught:
            client.templates.get("sumido")

        assert caught.value.status == 404
        assert caught.value.code == "not_found"
