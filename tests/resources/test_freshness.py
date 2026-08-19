"""Frescor da cópia."""

from __future__ import annotations

import pytest

from aronline import ApiError, Client
from tests.support.fake_api import FakeApi

FRESHNESS = {
    "refreshed_at": "2026-08-18T11:42:03-03:00",
    "last_load_at": "2026-08-18T11:40:00-03:00",
    "worst_lag_seconds": 34904,
    "tables_tracked": 46,
    "tables_never_loaded": 2,
    "behind": [{"legacy": "geral.ger_voz", "lag_seconds": 34904}],
}


class TestGet:
    def test_entrega_direto_porque_esta_rota_nao_envelopa(
        self, api: FakeApi, client: Client
    ) -> None:
        api.answers(FRESHNESS)

        assert client.freshness.get() == FRESHNESS
        assert api.received.path == "/v3/freshness"

    def test_exige_token_como_qualquer_rota_de_dado(self, anonymous: Client) -> None:
        with pytest.raises(ApiError) as caught:
            anonymous.freshness.get()

        assert caught.value.status == 401
        assert caught.value.code == "unauthenticated"

    def test_sync_nao_configurado_chega_como_503(self, api: FakeApi, client: Client) -> None:
        api.refuses(
            503,
            {"code": "unavailable", "message": "a leitura de sync.* não está configurada"},
            {"Retry-After": "60"},
        )

        with pytest.raises(ApiError) as caught:
            client.freshness.get()

        assert caught.value.status == 503
        assert caught.value.retry_after_seconds == 60
        assert caught.value.retryable is True
