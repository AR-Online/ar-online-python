"""Turning a refused response into an ``ApiError``."""

from __future__ import annotations

from typing import Any

from aronline.errors import ApiError

__all__ = ["to_api_error"]


def to_api_error(
    status: int,
    body: Any,
    request_id: str | None,
    retry_after: str | None,
) -> ApiError:
    """Build the error a refusal becomes.

    A refusal that does not carry the envelope is still a refusal: a proxy
    answering 502 in HTML has to fail the same way, or whoever hit it goes
    looking for a bug in their own parsing code.
    """
    envelope = _read_envelope(body)

    return ApiError(
        status=status,
        code=envelope.get("code") or "invalid_response",
        message=envelope.get("message") or f"a API respondeu {status} sem o corpo de erro esperado",
        request_id=envelope.get("request_id") or request_id,
        field=envelope.get("field"),
        details=envelope.get("details"),
        retry_after_seconds=_read_retry_after(retry_after),
    )


def _read_envelope(body: Any) -> dict[str, Any]:
    if not isinstance(body, dict):
        return {}

    error = body.get("error")

    return error if isinstance(error, dict) else {}


def _read_retry_after(header: str | None) -> float | None:
    """Seconds, or nothing.

    ``Retry-After`` also has an HTTP-date form. The API only ever sends
    seconds, so anything else is dropped rather than guessed at -- a wrong
    delay is worse than no delay.
    """
    if header is None:
        return None

    try:
        seconds = float(header)
    except ValueError:
        return None

    return seconds if seconds >= 0 else None
