"""What every resource shares: the transport, and nothing else."""

from __future__ import annotations

from aronline.http.transport import Transport

__all__ = ["Resource"]


class Resource:
    """Base of every resource."""

    def __init__(self, transport: Transport) -> None:
        self._transport = transport
