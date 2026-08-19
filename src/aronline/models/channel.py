"""The channels a template can belong to."""

from __future__ import annotations

from typing import Literal

__all__ = ["CHANNELS", "Channel"]

#: A channel accepted by the template filter.
Channel = Literal["email", "sms", "whatsapp", "voice", "letter"]

#: The same list at runtime, for anyone validating before calling.
#:
#: The list is closed on the server (decision A11): a value outside it answers
#: 400 ``invalid_value`` with the accepted ones in the message, never a silent
#: empty list.
CHANNELS: tuple[Channel, ...] = ("email", "sms", "whatsapp", "voice", "letter")
