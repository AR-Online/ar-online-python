"""The legacy gateway, as functions."""

from __future__ import annotations

import base64
import binascii
import urllib.parse
from typing import Any, cast

from aronline.legacy.errors import LegacyApiError
from aronline.legacy.models.envio import EnvioRequest, EnvioResponse
from aronline.legacy.models.regua import FinalizarReguaResult
from aronline.legacy.models.sending_proof import SendingProof
from aronline.legacy.resources.status import LegacyStatusResource
from aronline.legacy.resources.templates import LegacyTemplatesResource
from aronline.legacy.transport import LegacyTransport

__all__ = ["LegacyArea"]


class LegacyArea:
    """Everything docs.ar-online.com.br documents of the gateway, spoken exactly
    as the old API speaks it.

    ::

        from aronline import Client

        client = Client(legacy_token=os.environ["AR_GW_TOKEN"])
        sent = client.legacy.send({"nameTo": "João", "subject": "…", "content": "…"})
        status = client.legacy.status.email(sent["idEmail"])

    This area exists so an integration written against the old contract gets
    typed calls today. As /v3 grows an equivalent for a route, the function here
    swaps its transport without changing shape -- the migration happens under
    your feet, not in your code. Each function's documentation names its /v3
    equivalent when one exists.
    """

    def __init__(self, transport: LegacyTransport) -> None:
        self._transport = transport

        #: Per-channel status and the consolidated forensic view.
        self.status = LegacyStatusResource(transport)
        #: The gateway's template routes. The /v3 equivalent for reads is
        #: ``client.templates``.
        self.templates = LegacyTemplatesResource(transport)

    def send(self, envio: EnvioRequest) -> EnvioResponse:
        """Sends a notification -- ``POST /gw/email``, the multichannel route
        despite the name.

        Processing is asynchronous: keep the returned ``idEmail``, it is the
        handle for every status and proof question later.

        No /v3 equivalent yet.
        """
        return cast("EnvioResponse", self._transport.json("POST", "/gw/email", body=envio))

    def sending_proof(self, id_email: str) -> SendingProof:
        """The sending proof as a PDF.

        The wire carries it in base64 inside JSON; this decodes it for you and
        keeps the raw string reachable. While the e-mail has no delivery status
        the gateway answers a message instead, and ``pdf`` comes back ``None``
        -- ask again later. That is an answer, not a refusal.

        No /v3 equivalent yet.
        """
        body: Any = self._transport.json("GET", f"/gw/sending-proof/{_quote(id_email)}")
        content = body.get("content") if isinstance(body, dict) else None

        if not isinstance(content, str):
            message = body.get("message") if isinstance(body, dict) else None

            return {
                "pdf": None,
                "content_base64": None,
                "message": message if isinstance(message, str) else None,
            }

        return {"pdf": _decode_base64(content), "content_base64": content, "message": None}

    def laudo(self, id_email: str) -> bytes:
        """The expert-evidence report -- the one route that answers the PDF
        binary directly, no base64, no JSON.

        No /v3 equivalent yet.
        """
        return self._transport.binary(f"/gw/email/laudo/{_quote(id_email)}")

    def finalizar_regua(self, id_email: str) -> FinalizarReguaResult:
        """Stops the notification ladder for this send.

        A GET with a side effect -- that is the old contract, and the SDK does
        not "fix" it to POST. A caller who saw ``GET`` and assumed it was safe
        to repeat would be repeating a write.

        No /v3 equivalent yet.
        """
        return cast(
            "FinalizarReguaResult",
            self._transport.json("GET", f"/regua-notificacao/finalizar/{_quote(id_email)}"),
        )


def _quote(id_email: str) -> str:
    """Escaped, so a crooked id cannot become another path."""
    return urllib.parse.quote(id_email, safe="")


def _decode_base64(content: str) -> bytes:
    """The proof, decoded, or the SDK's own error.

    ``validate=True`` on purpose: without it, base64 that is not base64 decodes
    to garbage bytes, and the caller writes a corrupt PDF to disk instead of
    finding out that the gateway answered something unexpected.
    """
    try:
        return base64.b64decode(content, validate=True)
    except (binascii.Error, ValueError) as error:
        raise LegacyApiError(
            status=200,
            http_status=200,
            message="o comprovante veio com base64 ilegível",
            body={"content": content},
        ) from error
