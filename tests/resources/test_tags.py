"""Etiquetas."""

from __future__ import annotations

import pytest

from aronline import ApiError, Client
from tests.support.fake_api import FakeApi

TAG = {
    "id": "12",
    "name": "urgente",
    "color": "#ff0000",
    "created_at": "2024-10-12T14:11:13-03:00",
}


class TestList:
    def test_devolve_as_etiquetas_desembrulhadas(self, api: FakeApi, client: Client) -> None:
        api.answers({"data": [TAG]})

        assert client.tags.list() == [TAG]
        assert api.received.path == "/v3/tags"

    def test_token_de_integracao_recebe_403_e_nao_lista_vazia(
        self, api: FakeApi, client: Client
    ) -> None:
        api.refuses(
            403,
            {
                "code": "forbidden",
                "message": "Esta rota responde a token de pessoa: etiquetas são pessoais.",
            },
        )

        with pytest.raises(ApiError) as caught:
            client.tags.list()

        assert caught.value.status == 403
        assert caught.value.code == "forbidden"


class TestGet:
    def test_busca_uma_etiqueta(self, api: FakeApi, client: Client) -> None:
        api.answers({"data": TAG})

        assert client.tags.get("12") == TAG
        assert api.received.path == "/v3/tags/12"

    def test_etiqueta_que_nao_e_sua_chega_como_404(self, api: FakeApi, client: Client) -> None:
        api.refuses(404, {"code": "not_found", "message": "Etiqueta não encontrada."})

        with pytest.raises(ApiError) as caught:
            client.tags.get("999")

        assert caught.value.status == 404
