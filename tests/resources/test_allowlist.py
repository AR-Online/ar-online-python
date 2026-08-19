"""Lista de permitidos."""

from __future__ import annotations

import pytest

from aronline import ApiError, Client
from tests.support.fake_api import FakeApi

ENTRY = {
    "id": "7",
    "recipient": "alguem@exemplo.com.br",
    "created_at": "2024-10-12T14:11:13-03:00",
}


class TestList:
    def test_devolve_os_permitidos_desembrulhados(self, api: FakeApi, client: Client) -> None:
        api.answers({"data": [ENTRY]})

        assert client.allowlist.list() == [ENTRY]
        assert api.received.path == "/v3/allowlist"

    def test_token_de_integracao_recebe_403(self, api: FakeApi, client: Client) -> None:
        api.refuses(
            403,
            {
                "code": "forbidden",
                "message": "Esta rota responde a token de pessoa: a lista é pessoal.",
            },
        )

        with pytest.raises(ApiError) as caught:
            client.allowlist.list()

        assert caught.value.status == 403
