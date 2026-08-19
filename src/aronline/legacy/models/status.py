"""The per-channel status answers of ``GET /gw/<canal>/{idEmail}``.

This family says "not yet" four different ways -- ``""``, ``null``, a key that
vanishes, ``{}`` -- sometimes two of them in the same response. The types keep
each convention where the wire has it, and the two that look alike in Python
stay apart: a key that vanishes is a non-required key, and one that comes
``null`` is ``| None``. Normalizing them would break the fidelity the legacy
area exists to give.

In every route the id is the notification's uuid -- the e-mail's. There is no
per-channel id.

Dates come as ``"18/07/2026 01:01:32"``, with no zone, and stay ``str``. The
format does not give an unambiguous instant, so a ``datetime`` built here would
be a guess wearing a precise type.
"""

from __future__ import annotations

from typing import Any, TypedDict

__all__ = [
    "SmsAnswer",
    "StatusCarta",
    "StatusEmail",
    "StatusSms",
    "StatusVoz",
    "StatusWhatsapp",
]

#: One entry of :attr:`StatusSms.answered`. The old documentation says list of
#: strings; the wire carries **objects**, and whoever integrated read the
#: objects -- so the object is what stays.
SmsAnswer = dict[str, Any]


class _StatusEmailRequired(TypedDict):
    """The keys the e-mail status always carries."""

    #: ``""`` until it happens -- not ``None``, and not a missing key.
    dateSend: str
    #: ``""`` until it happens.
    dateDelivery: str
    #: ``None`` until it happens. Same meaning as the ``""`` above, different
    #: convention: testing ``is None`` on all four misses half of them.
    dateReading: str | None
    dateAcceptance: str | None
    error: bool
    #: Climbs with the stage reached: ``Processado``, ``Enviado``, ``Entregue``, ``Lido``.
    description: str
    failureReason: str | None
    customID: str | None
    idEmail: str


class StatusEmail(_StatusEmailRequired, total=False):
    """Status do AR-Email."""

    #: The full description of the failure; filled in together with ``failureReason``.
    failureReasonDescription: str | None


class StatusSms(TypedDict):
    """Status do AR-SMS."""

    #: ``Lido (acessou o link)`` beats every other label when the link was opened.
    description: str
    #: ``""`` until it happens.
    dateSend: str
    dateReading: str | None
    dateAnswered: str | None
    #: A list of **objects**, not of strings.
    answered: list[SmsAnswer]


class _StatusWhatsappRequired(TypedDict):
    """The keys the WhatsApp status always carries."""

    description: str
    error: bool
    failureReason: str | None
    #: Always ``None`` on this route, even when the message has one -- read it
    #: on the e-mail route.
    customID: str | None
    idEmail: str


class StatusWhatsapp(_StatusWhatsappRequired, total=False):
    """Status do AR-WhatsApp.

    The dates that have not happened **vanish** from the response instead of
    coming ``None`` -- hence the non-required keys. ``"dateDelivery" in status``
    is the question to ask here, not ``status["dateDelivery"] is None``.
    """

    dateSent: str
    dateDelivery: str
    dateResponse: str
    dateAccessLink: str


class _StatusVozRequired(TypedDict):
    """The one key the voice status always carries."""

    description: str


class StatusVoz(_StatusVozRequired, total=False):
    """Status do AR-Voz.

    The one route that never answers 404: an unknown uuid gets a 200 with only
    ``description`` -- ``Não há registro de voz para este envio``. That is an
    answer, not a refusal, and the SDK does not turn it into one.

    When a call failed before succeeding, the answer tells only the failure:
    ``dateSuccessCall`` never travels together with ``dateFailureCall``.
    """

    dateSent: str
    dateSuccessCall: str
    dateFailureCall: str
    #: The recording's link -- depends on a data load that may lag behind.
    linkCall: str


class _StatusCartaRequired(TypedDict):
    """The keys the letter status always carries."""

    description: str
    error: bool


class StatusCarta(_StatusCartaRequired, total=False):
    """Status do AR-Cartas.

    Two stages change name on the way out: the provider produces
    ``datePrepared`` and ``dateDelivered``, the response carries
    ``datePreparation`` and ``dateDelivery``. The provider's names never reach
    the client.
    """

    dateProcessing: str
    datePreparation: str
    dateSent: str
    dateDelivery: str
    #: The Correios tracking code.
    sro: str
    linkArCartaComprovante: str
    linkRastreio: str
