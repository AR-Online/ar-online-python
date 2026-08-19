"""A real server on a real port, not a stubbed opener.

What this SDK has to get right IS the wire: which routes wrap their answer,
how a refusal comes back, what happens when something that is not the API
answers. A stubbed opener would only prove that the code calls the stub.
"""

from __future__ import annotations

import json
import threading
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

__all__ = ["FakeApi", "Received"]


@dataclass
class Received:
    """What the fake saw."""

    method: str
    path: str
    authorization: str | None
    accept: str | None


@dataclass
class _Reply:
    status: int = 200
    body: str = "{}"
    content_type: str = "application/json"
    headers: dict[str, str] = field(default_factory=dict)


class FakeApi:
    """A one-request-at-a-time stand-in for the API."""

    def __init__(self) -> None:
        self._reply = _Reply()
        self._received: Received | None = None
        self._server: HTTPServer | None = None
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        fake = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                fake._received = Received(
                    method=self.command,
                    path=self.path,
                    authorization=self.headers.get("Authorization"),
                    accept=self.headers.get("Accept"),
                )

                reply = fake._reply
                payload = reply.body.encode("utf-8")

                self.send_response(reply.status)
                self.send_header("Content-Type", reply.content_type)
                self.send_header("Content-Length", str(len(payload)))
                self.send_header("X-Request-Id", "req-do-cabecalho")

                for name, value in reply.headers.items():
                    self.send_header(name, value)

                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, *_: Any) -> None:
                """Quiet: the suite's output is the assertions, not the access log."""

        self._server = HTTPServer(("127.0.0.1", 0), Handler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
            self._server = None

        if self._thread is not None:
            self._thread.join(timeout=5)
            self._thread = None

    @property
    def base_url(self) -> str:
        """Where the fake is listening."""
        if self._server is None:
            raise RuntimeError("o servidor de mentira não está no ar")

        host, port = self._server.server_address[:2]

        return f"http://{host!s}:{port}"

    @property
    def received(self) -> Received:
        """The request the fake last saw."""
        if self._received is None:
            raise AssertionError("nenhuma requisição chegou ao servidor de mentira")

        return self._received

    def answers(self, body: Any) -> None:
        """Answer this JSON body with 200."""
        self._reply = _Reply(body=json.dumps(body))

    def refuses(
        self,
        status: int,
        error: dict[str, Any],
        headers: dict[str, str] | None = None,
    ) -> None:
        """Answer the catalog's error envelope with a status."""
        self._reply = _Reply(
            status=status,
            body=json.dumps({"error": error}),
            headers=headers or {},
        )

    def answers_raw(self, status: int, body: str, content_type: str = "text/html") -> None:
        """Answer something that is not JSON -- a proxy in the middle."""
        self._reply = _Reply(status=status, body=body, content_type=content_type)
