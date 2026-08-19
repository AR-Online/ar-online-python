"""The fake API, up for the whole session and reset per test."""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from aronline import Client, LegacyArea
from tests.support.fake_api import FakeApi


@pytest.fixture(scope="session")
def api() -> Iterator[FakeApi]:
    fake = FakeApi()
    fake.start()

    yield fake

    fake.stop()


@pytest.fixture
def client(api: FakeApi) -> Client:
    """A client pointed at the fake, with a token."""
    return Client(token="tok", base_url=api.base_url)


@pytest.fixture
def anonymous(api: FakeApi) -> Client:
    """A client with no credential -- only the open route works on it."""
    return Client(base_url=api.base_url)


@pytest.fixture
def legacy(api: FakeApi) -> LegacyArea:
    """The legacy area of a client pointed at the fake, with the gateway credential."""
    return Client(legacy_base_url=api.base_url, legacy_token="tok-gw").legacy
