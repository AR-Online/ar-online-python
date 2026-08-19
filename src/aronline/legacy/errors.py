"""What a refusal from the legacy gateway looks like on this side."""

from __future__ import annotations

from typing import Any

__all__ = ["LegacyApiError"]


class LegacyApiError(Exception):
    """A refusal from the legacy gateway, raised so a failed call cannot pass
    for a good one.

    The gateway has two ways of saying no: an HTTP status with a
    ``{"statusCode": …, "message": …}`` body, and -- in the templates family --
    an HTTP 200 whose real code hides inside the ``{"data": …, "statusCode": …}``
    envelope. Both arrive here, so a caller has one type to catch.

    It is deliberately a different type from ``ApiError``: the /v3 error carries
    a catalog ``code`` and a ``request_id``, and the old gateway has neither.
    One class with half its fields always empty would promise data that does not
    exist on this surface.
    """

    def __init__(
        self,
        *,
        status: int,
        http_status: int,
        message: str,
        body: Any = None,
    ) -> None:
        super().__init__(message)

        #: The code that matters: the envelope's inner ``statusCode`` when the
        #: refusal came wrapped, the HTTP status otherwise. Zero when the
        #: gateway was never reached.
        self.status = status
        #: What the wire said -- ``200`` when the envelope hid a ``404``. Zero
        #: when the call never left this process.
        self.http_status = http_status
        #: The message the gateway sent, in pt-BR, or the SDK's own when the
        #: gateway sent none.
        self.message = message
        #: The body exactly as it came, for whoever needs the raw contract.
        #: ``None`` when there was no body to read.
        self.body = body

    def __repr__(self) -> str:
        return (
            f"LegacyApiError(status={self.status}, "
            f"http_status={self.http_status}, message={self.message!r})"
        )
