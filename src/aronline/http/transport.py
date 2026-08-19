"""The HTTP layer, and the only place in the SDK that knows it exists."""

from __future__ import annotations

import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from aronline.errors import ApiError
from aronline.http.error_envelope import to_api_error
from aronline.http.json_body import UNPARSED, parse_json

__all__ = ["DEFAULT_BASE_URL", "DEFAULT_TIMEOUT", "Transport"]

#: Where /v3 lives. Override it for staging or for a local process.
DEFAULT_BASE_URL = "https://v3.ar-online.com.br"

#: How long a call waits before giving up, in seconds.
DEFAULT_TIMEOUT = 30.0


class Transport:
    """Builds the request, reads the answer, and raises what went wrong.

    Everything above it -- the resources, the client -- deals in functions and
    dictionaries. That is the whole point of the package: whoever installs it
    should never build a URL, set a header, read a status or unwrap an
    envelope.

    It uses ``urllib`` from the standard library on purpose: an SDK with no
    dependencies is one that never conflicts with what the application already
    pinned.
    """

    def __init__(
        self,
        *,
        token: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        opener: urllib.request.OpenerDirector | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._token = token
        self._timeout = timeout
        self._opener = opener or urllib.request.build_opener()

    def envelope(
        self,
        path: str,
        *,
        query: dict[str, str | None] | None = None,
        authenticated: bool = True,
    ) -> Any:
        """For the routes that answer ``{"data": ...}`` -- templates, tags, allowlist.

        Not every route wraps its answer, which is the one trap of this API:
        freshness and version answer the object itself. Unwrapping all of them,
        or none, breaks half the calls, so the choice is made per route by
        whichever method the resource calls.
        """
        body = self.bare(path, query=query, authenticated=authenticated)

        if not isinstance(body, dict) or "data" not in body:
            raise ApiError(
                status=200,
                code="invalid_response",
                message=f"{path} respondeu sem o envelope 'data' que a rota promete",
                request_id=None,
            )

        return body["data"]

    def bare(
        self,
        path: str,
        *,
        query: dict[str, str | None] | None = None,
        authenticated: bool = True,
    ) -> Any:
        """For the routes that answer the object directly -- freshness, version."""
        # Refused here, before the socket: a 401 round trip teaches nothing
        # that the missing token does not already say.
        if authenticated and self._token is None:
            raise ApiError(
                status=401,
                code="unauthenticated",
                message=f"{path} exige um token; construa o cliente com token=...",
                request_id=None,
            )

        request = urllib.request.Request(
            self.url(path, query),
            method="GET",
            headers=self._headers(authenticated),
        )

        status, text, headers = self._send(request)
        body = parse_json(text)
        request_id = headers.get("X-Request-Id")

        if status >= 400:
            raise to_api_error(status, body, request_id, headers.get("Retry-After"))

        # A 200 that is not JSON is something other than the API answering. It
        # fails like any other refusal -- a raw JSONDecodeError leaking out
        # here would send whoever hit it looking for a bug in their own code.
        if body is UNPARSED:
            raise ApiError(
                status=status,
                code="invalid_response",
                message="a resposta não é JSON — algo respondeu no lugar da API",
                request_id=request_id,
            )

        return body

    def url(self, path: str, query: dict[str, str | None] | None = None) -> str:
        """The absolute URL of a path. Exposed because the tests assert on it."""
        filled = {key: value for key, value in (query or {}).items() if value is not None}
        suffix = f"?{urllib.parse.urlencode(filled)}" if filled else ""

        return f"{self._base_url}{path}{suffix}"

    def _headers(self, authenticated: bool) -> dict[str, str]:
        headers = {"Accept": "application/json"}

        if authenticated and self._token is not None:
            headers["Authorization"] = f"Bearer {self._token}"

        return headers

    def _send(self, request: urllib.request.Request) -> tuple[int, str, Any]:
        try:
            with self._opener.open(request, timeout=self._timeout) as response:
                return response.status, _read(response), response.headers
        except urllib.error.HTTPError as error:
            # urllib raises on 4xx and 5xx. They are answers, not failures:
            # the body carries the catalog, and the caller needs it.
            with error:
                return error.code, _read(error), error.headers
        except (urllib.error.URLError, OSError) as error:
            # Timeout and connection refused arrive as opaque platform errors.
            # They become the SDK's own error so a caller has one type to catch
            # instead of three.
            raise ApiError(
                status=0,
                code="unreachable",
                message=f"não foi possível falar com {self._base_url}: {error}",
                request_id=None,
            ) from error


def _read(response: Any) -> str:
    payload: bytes = response.read()

    return payload.decode("utf-8", errors="replace")
