"""The consolidated answer of ``GET /gw/full/{idEmail}``.

Every channel's forensic data in one call.
"""

from __future__ import annotations

from typing import Any, TypedDict

__all__ = ["FullChannelDetail", "StatusEvent", "StatusFull", "StatusHistory", "StatusLast"]

#: A channel's detail block inside the full status.
FullChannelDetail = dict[str, Any]


class StatusEvent(TypedDict):
    """One status event: the label and when it happened, in BRT."""

    label: str
    #: ``dd/mm/aaaa hh:mm:ss``, Brasília time. Fields suffixed ``UTC`` elsewhere
    #: carry the same instant in UTC.
    dateTime: str


class StatusHistory(TypedDict, total=False):
    """The full status history of each channel. A channel not used is absent."""

    email: list[StatusEvent]
    sms: list[StatusEvent]
    whatsapp: list[StatusEvent]
    voz: list[StatusEvent]
    carta: list[StatusEvent]


class StatusLast(TypedDict, total=False):
    """Each channel's latest status. A channel not used is absent."""

    email: StatusEvent
    sms: StatusEvent
    whatsapp: StatusEvent
    voz: StatusEvent
    carta: StatusEvent


class StatusFull(TypedDict):
    """Status completo -- the forensic view.

    ``statusFull`` and ``lastStatus`` are typed precisely; the per-channel
    detail lists are passed through as they come. They carry the
    expert-evidence material -- signed timestamps, reading trails,
    geolocation -- in provider-shaped nests that the public documentation shows
    by example rather than by schema, and a type invented on top of an example
    would promise fields this SDK has never proven.
    """

    #: The e-mail's internal numeric code on the platform.
    codEmail: int
    statusFull: StatusHistory
    lastStatus: StatusLast
    email: list[FullChannelDetail]
    sms: list[FullChannelDetail]
    whatsapp: list[FullChannelDetail]
    voz: list[FullChannelDetail]
    carta: list[FullChannelDetail]
