"""The one place that knows how the legacy gateway talks."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from aronline.http.json_body import UNPARSED, parse_json
from aronline.http.transport import DEFAULT_TIMEOUT
from aronline.legacy.errors import LegacyApiError

__all__ = ["DEFAULT_LEGACY_BASE_URL", "LegacyTransport"]

#: Where the legacy gateway lives. Override it for staging or for a local
#: process. It is independent of the /v3 address: the two surfaces are two
#: deployments, and pointing one at a test environment must not move the other.
DEFAULT_LEGACY_BASE_URL = "https://api.ar-online.com.br"


class LegacyTransport:
    """Builds the request, reads the answer, and raises what went wrong.

    Two things make this a different transport from the /v3 one rather than a
    flag on the same one. The credential goes **raw** in ``authorization`` --
    no ``Bearer`` -- and success is not the HTTP status: the templates family
    answers 200 with the real code inside the body, and the voice status
    answers 200 with a sentence where the other channels answer 404. Each
    method here decides by the contract of the route that calls it.
    """

    def __init__(
        self,
        *,
        token: str | None = None,
        base_url: str = DEFAULT_LEGACY_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        opener: urllib.request.OpenerDirector | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._token = token
        self._timeout = timeout
        self._opener = opener or urllib.request.build_opener()

    def json(
        self,
        method: str,
        path: str,
        *,
        query: dict[str, str | None] | None = None,
        body: Any = None,
    ) -> Any:
        """For the routes that answer JSON and refuse with an HTTP status."""
        _status, parsed = self._exchange(method, path, query=query, body=body)

        return parsed

    def gw_envelope(
        self,
        method: str,
        path: str,
        *,
        query: dict[str, str | None] | None = None,
        body: Any = None,
    ) -> Any:
        """For the ``/gw/templates`` family, which wraps everything in
        ``{"data": …, "statusCode": …}`` and answers **HTTP 200 even on error**.

        The code that matters is the inner one. Reading only the HTTP status is
        the single most common integration bug against this family, and
        unwrapping it here is exactly what the legacy area abstracts.
        """
        http_status, parsed = self._exchange(method, path, query=query, body=body)

        if not isinstance(parsed, dict) or "data" not in parsed:
            raise LegacyApiError(
                status=http_status,
                http_status=http_status,
                message=f"{path} respondeu sem o envelope 'data' que a família promete",
                body=parsed,
            )

        data = parsed["data"]
        inner = _read_inner_status(parsed)

        if inner >= 400:
            raise LegacyApiError(
                status=inner,
                http_status=http_status,
                message=_read_envelope_error(data) or f"o gateway recusou com {inner}",
                body=parsed,
            )

        return data

    def binary(self, path: str) -> bytes:
        """For the one route that answers a file instead of JSON -- the laudo."""
        status, payload, _headers = self._send("GET", path)

        if status >= 400:
            raise _refusal(status, parse_json(payload.decode("utf-8", errors="replace")))

        return payload

    def url(self, path: str, query: dict[str, str | None] | None = None) -> str:
        """The absolute URL of a path. Exposed because the tests assert on it."""
        filled = {key: value for key, value in (query or {}).items() if value is not None}
        suffix = f"?{urllib.parse.urlencode(filled)}" if filled else ""

        return f"{self._base_url}{path}{suffix}"

    def _exchange(
        self,
        method: str,
        path: str,
        *,
        query: dict[str, str | None] | None,
        body: Any,
    ) -> tuple[int, Any]:
        status, payload, _headers = self._send(method, path, query=query, body=body)
        parsed = parse_json(payload.decode("utf-8", errors="replace"))

        if status >= 400:
            raise _refusal(status, parsed)

        # A 200 that is not JSON is something other than the gateway answering.
        # A raw JSONDecodeError leaking out here would send whoever hit it
        # looking for a bug in their own code.
        if parsed is UNPARSED:
            raise LegacyApiError(
                status=status,
                http_status=status,
                message="a resposta não é JSON — algo respondeu no lugar do gateway",
            )

        return status, parsed

    def _send(
        self,
        method: str,
        path: str,
        *,
        query: dict[str, str | None] | None = None,
        body: Any = None,
    ) -> tuple[int, bytes, Any]:
        # Refused here, before the socket: a 401 round trip teaches nothing that
        # the missing token does not already say. Every legacy route needs the
        # credential -- the gateway has no open route.
        if self._token is None:
            raise LegacyApiError(
                status=401,
                http_status=0,
                message=f"{path} exige o token do gateway; construa o cliente com legacy_token=...",
            )

        data = None if body is None else json.dumps(body).encode("utf-8")

        # Raw on purpose: the gateway wants the JWT without `Bearer`, the exact
        # opposite of /v3. Prefixing it here would turn every call into the
        # gateway's own 401.
        headers = {"Accept": "application/json", "authorization": self._token}

        if data is not None:
            headers["Content-Type"] = "application/json"

        request = urllib.request.Request(
            self.url(path, query),
            method=method,
            headers=headers,
            data=data,
        )

        try:
            with self._opener.open(request, timeout=self._timeout) as response:
                payload: bytes = response.read()

                return response.status, payload, response.headers
        except urllib.error.HTTPError as error:
            # urllib raises on 4xx and 5xx. They are answers, not failures: the
            # body carries the gateway's message, and the caller needs it.
            with error:
                return error.code, error.read(), error.headers
        except (urllib.error.URLError, OSError) as error:
            # Timeout and connection refused arrive as opaque platform errors.
            # They become the SDK's own error so a caller has one type to catch
            # instead of three.
            raise LegacyApiError(
                status=0,
                http_status=0,
                message=f"não foi possível falar com {self._base_url}: {error}",
            ) from error


def _refusal(http_status: int, body: Any) -> LegacyApiError:
    """An HTTP-level refusal -- ``{"statusCode", "message"}``, or whatever a proxy sent."""
    shape = body if isinstance(body, dict) else {}
    inner = shape.get("statusCode")
    message = shape.get("message")

    return LegacyApiError(
        status=inner if isinstance(inner, int) else http_status,
        http_status=http_status,
        message=message
        if isinstance(message, str)
        else f"o gateway respondeu {http_status} sem o corpo de erro esperado",
        body=None if body is UNPARSED else body,
    )


def _read_inner_status(envelope: dict[str, Any]) -> int:
    """The code that matters. Absent means the family answered plainly -- a 200."""
    inner = envelope.get("statusCode")

    return inner if isinstance(inner, int) else 200


def _read_envelope_error(data: Any) -> str | None:
    """The family's error message sits inside ``data``: ``{"error": "…"}``.

    Anything else stays raw on the error's ``body`` for the caller to read.
    """
    if not isinstance(data, dict):
        return None

    error = data.get("error")

    return error if isinstance(error, str) else None
