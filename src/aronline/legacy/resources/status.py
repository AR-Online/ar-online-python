"""What happened to this notification, one route per channel."""

from __future__ import annotations

import urllib.parse
from typing import cast

from aronline.legacy.models.full import StatusFull
from aronline.legacy.models.status import (
    StatusCarta,
    StatusEmail,
    StatusSms,
    StatusVoz,
    StatusWhatsapp,
)
from aronline.legacy.resources.base import LegacyResource

__all__ = ["LegacyStatusResource"]


class LegacyStatusResource(LegacyResource):
    """The most used surface of the old API.

    Every method takes the same id: the notification's uuid, the one ``send()``
    answered. Asking for the SMS is asking for the SMS *of that notification*;
    there is no per-channel id to keep.

    An unknown id answers 404 and arrives as a ``LegacyApiError`` -- except on
    :meth:`voz`, where the old API answers 200 with a sentence, and so does this.

    No /v3 equivalent yet for any of these.
    """

    def email(self, id_email: str) -> StatusEmail:
        """When it went out, when the recipient's server accepted it, when it
        was read."""
        return cast("StatusEmail", self._transport.json("GET", f"/gw/email/{_quote(id_email)}"))

    def sms(self, id_email: str) -> StatusSms:
        """What happened to the SMS, and the recipient's answers when there were any."""
        return cast("StatusSms", self._transport.json("GET", f"/gw/sms/{_quote(id_email)}"))

    def whatsapp(self, id_email: str) -> StatusWhatsapp:
        """The WhatsApp leg. Dates that have not happened are absent keys, not ``None``."""
        return cast(
            "StatusWhatsapp", self._transport.json("GET", f"/gw/whatsapp/{_quote(id_email)}")
        )

    def voz(self, id_email: str) -> StatusVoz:
        """Never a 404: no record answers 200 with only a ``description``."""
        return cast("StatusVoz", self._transport.json("GET", f"/gw/voz/{_quote(id_email)}"))

    def carta(self, id_email: str) -> StatusCarta:
        """The letter's stages, preparation to delivery, with the Correios tracking."""
        return cast("StatusCarta", self._transport.json("GET", f"/gw/carta/{_quote(id_email)}"))

    def full(self, id_email: str) -> StatusFull:
        """Every channel's forensic data in one call.

        For following a single channel's current stage, the per-channel routes
        are the lighter ask.
        """
        return cast("StatusFull", self._transport.json("GET", f"/gw/full/{_quote(id_email)}"))


def _quote(id_email: str) -> str:
    """Escaped, so a crooked id cannot become another path."""
    return urllib.parse.quote(id_email, safe="")
