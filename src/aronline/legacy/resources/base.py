"""What every legacy resource shares: the legacy transport, and nothing else."""

from __future__ import annotations

from aronline.legacy.transport import LegacyTransport

__all__ = ["LegacyResource"]


class LegacyResource:
    """Base of every resource in the legacy area."""

    def __init__(self, transport: LegacyTransport) -> None:
        self._transport = transport
