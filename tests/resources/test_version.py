"""Versão — a única rota aberta."""

from __future__ import annotations

from aronline import Client
from tests.support.fake_api import FakeApi

VERSION = {
    "version": "0.1.0",
    "min_migration": "0025_credentials.sql",
    "environment": "local",
}


class TestGet:
    def test_responde_sem_token(self, api: FakeApi, anonymous: Client) -> None:
        api.answers(VERSION)

        assert anonymous.version.get() == VERSION
        assert api.received.path == "/v3/version"
        assert api.received.authorization is None

    def test_nao_manda_o_token_nem_quando_o_cliente_tem_um(
        self, api: FakeApi, client: Client
    ) -> None:
        api.answers(VERSION)

        client.version.get()

        assert api.received.authorization is None
