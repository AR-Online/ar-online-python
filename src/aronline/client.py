"""The client -- the one thing you construct."""

from __future__ import annotations

import urllib.request

from aronline.http.transport import DEFAULT_BASE_URL, DEFAULT_TIMEOUT, Transport
from aronline.legacy.area import LegacyArea
from aronline.legacy.transport import DEFAULT_LEGACY_BASE_URL, LegacyTransport
from aronline.resources.allowlist import AllowlistResource
from aronline.resources.freshness import FreshnessResource
from aronline.resources.tags import TagsResource
from aronline.resources.templates import TemplatesResource
from aronline.resources.version import VersionResource

__all__ = ["Client"]


class Client:
    """The AR Online API client.

    ::

        from aronline import Client

        client = Client(token=os.environ["AR_TOKEN"])
        templates = client.templates.list(channel="whatsapp")

    It owns the transport and hands it to each resource; the resources are the
    public surface. Nothing above this line knows that HTTP is involved.

    ``client.legacy`` is the second surface: the old gateway's contract, spoken
    exactly as documented, with its own address and its own credential
    (``legacy_token``). It exists so an integration on the old API gets typed
    calls today and migrates to /v3 by SDK update, not by rewrite.

    Each credential is optional: pass only the one for the surface you use.
    Neither leaks into the other's calls.
    """

    def __init__(
        self,
        *,
        token: str | None = None,
        legacy_token: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        legacy_base_url: str = DEFAULT_LEGACY_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        opener: urllib.request.OpenerDirector | None = None,
    ) -> None:
        transport = Transport(
            token=token,
            base_url=base_url,
            timeout=timeout,
            opener=opener,
        )
        legacy_transport = LegacyTransport(
            token=legacy_token,
            base_url=legacy_base_url,
            timeout=timeout,
            opener=opener,
        )

        #: Message templates.
        self.templates = TemplatesResource(transport)
        #: Your labels.
        self.tags = TagsResource(transport)
        #: Your allowed recipients.
        self.allowlist = AllowlistResource(transport)
        #: How fresh the copy of the data is.
        self.freshness = FreshnessResource(transport)
        #: Which version is running. The one route that needs no token.
        self.version = VersionResource(transport)
        #: The legacy gateway surface -- today's contract, idiosyncrasies included.
        self.legacy = LegacyArea(legacy_transport)
