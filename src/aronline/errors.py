"""What a refusal from the API looks like on this side."""

from __future__ import annotations

from typing import TypedDict

__all__ = ["ApiError", "ErrorDetail"]


class ErrorDetail(TypedDict):
    """One field-level complaint inside a validation error."""

    field: str
    code: str
    message: str


class ApiError(Exception):
    """A refusal from the API, raised so a failed call cannot pass for a good one.

    ``request_id`` is a first-class attribute on purpose: it is the first thing
    support asks for, and an SDK that swallowed it would force whoever hit the
    failure to reproduce it with curl just to find the number.
    """

    def __init__(
        self,
        *,
        status: int,
        code: str,
        message: str,
        request_id: str | None,
        field: str | None = None,
        details: list[ErrorDetail] | None = None,
        retry_after_seconds: float | None = None,
    ) -> None:
        super().__init__(message)

        #: The HTTP status. Zero when the API was never reached.
        self.status = status
        #: The catalog code -- ``not_found``, ``forbidden``, ``rate_limited``, ...
        self.code = code
        #: The message the API sent, in pt-BR.
        self.message = message
        #: From the error body, or from the ``X-Request-Id`` header when absent.
        self.request_id = request_id
        #: The field at fault, when the refusal is about one.
        self.field = field
        #: One entry per rejected field, on validation errors.
        self.details = details
        #: From the ``Retry-After`` header, on 429 and 503.
        self.retry_after_seconds = retry_after_seconds

    @property
    def retryable(self) -> bool:
        """True for the statuses the API says are worth trying again."""
        return self.status in (429, 503)

    def __repr__(self) -> str:
        return f"ApiError(status={self.status}, code={self.code!r}, request_id={self.request_id!r})"
