"""The recipients allowed to receive messages."""

from __future__ import annotations

from typing import cast

from aronline.models.allowlist_entry import AllowlistEntry
from aronline.resources.base import Resource

__all__ = ["AllowlistResource"]


class AllowlistResource(Resource):
    """The allowed recipients.

    The legacy called this a whitelist and answered it under the key ``leads``,
    a copy-paste that became contract. Here it is an allowlist, and the name
    says what the list holds. Like labels, it is personal -- an integration
    token gets 403.
    """

    def list(self) -> list[AllowlistEntry]:
        """Your allowed recipients, ordered by recipient."""
        return cast("list[AllowlistEntry]", self._transport.envelope("/v3/allowlist"))
