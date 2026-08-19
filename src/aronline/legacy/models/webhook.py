"""The webhook payload types.

The SDK does not receive HTTP for you -- webhooks arrive at *your* endpoint.
These are the payload shapes, exported so whoever receives them does not have
to type the contract by hand.
"""

from __future__ import annotations

from typing import Literal, TypedDict

from aronline.legacy.models.status import (
    StatusCarta,
    StatusEmail,
    StatusSms,
    StatusVoz,
    StatusWhatsapp,
)

__all__ = [
    "WebhookChannel",
    "WebhookMetadata",
    "WebhookPayloadV1",
    "WebhookPayloadV2",
    "WebhookStatusPayload",
]

#: The channels a webhook event names.
WebhookChannel = Literal["email", "sms", "whatsapp", "voz", "carta"]

#: The channel's own status answer, carried inside the v2 payload. Narrow it by
#: the event's ``channel`` before reading channel-specific keys.
WebhookStatusPayload = StatusEmail | StatusSms | StatusWhatsapp | StatusVoz | StatusCarta


class WebhookPayloadV1(TypedDict):
    """The default payload, delivered unless v2 was enabled with support.

    On failure events the three dates come ``None`` together.
    """

    #: The notification's uuid -- the same ``idEmail`` the API answers on send.
    notificationID: str
    channel: str
    description: str
    dateSent: str | None
    dateDelivery: str | None
    dateRead: str | None
    logDate: str


class WebhookMetadata(TypedDict):
    """The delivery bookkeeping of a v2 event."""

    webhookVersion: Literal["v2"]
    #: Delivery attempt -- up to 4 with the retry schedule.
    attempt: int


class _WebhookPayloadV2Required(TypedDict):
    """The keys a v2 event always carries."""

    eventVersion: str
    #: ISO 8601 timestamp of the event itself.
    occurredAt: str
    #: The notification's uuid -- the same ``idEmail`` the API answers on send.
    notificationID: str
    channel: WebhookChannel
    status: str
    payload: WebhookStatusPayload
    metadata: WebhookMetadata


class WebhookPayloadV2(_WebhookPayloadV2Required, total=False):
    """The enriched payload, enabled by asking support."""

    statusTimestamp: str
