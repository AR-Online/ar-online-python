"""The send contract of ``POST /gw/email``.

The field names are the gateway's, Portuguese and all. The legacy area keeps
the old vocabulary on purpose: an English rendition invented here would create
names that exist in no documentation anywhere.

Every block is optional on the way in, so the request types are ``total=False``
except for the three fields the route always requires.
"""

from __future__ import annotations

from typing import Any, Literal, TypedDict

__all__ = [
    "SMS_TYPE_SENDS",
    "Anexo",
    "CanalCarta",
    "CanalSms",
    "CanalVoz",
    "CanalWhatsapp",
    "EnvioRequest",
    "EnvioResponse",
    "EnvioValidation",
    "SmsTypeSend",
]


class Anexo(TypedDict):
    """An attachment, carried inline as base64."""

    name: str
    base64: str


class EnvioValidation(TypedDict, total=False):
    """Question/answer gate on the notification's page. Needs prior enablement."""

    question: str
    reply: str


#: When the SMS goes out: ``"1"`` (the default) only if the e-mail is not
#: sent/delivered, ``"2"`` always.
SmsTypeSend = Literal["1", "2"]

#: The same list at runtime, for anyone validating before calling.
SMS_TYPE_SENDS: tuple[SmsTypeSend, ...] = ("1", "2")


class CanalSms(TypedDict, total=False):
    """The SMS leg of a send."""

    #: The mobile number, digits only.
    number: str
    typeSend: SmsTypeSend
    #: Up to 140 characters; ``{SHORT_LINK}`` is expanded by the gateway.
    customMessage: str


class CanalWhatsapp(TypedDict, total=False):
    """The WhatsApp leg of a send."""

    number: str
    #: The custom template's variables, including the ``template`` identifier.
    variables: dict[str, Any]


class CanalVoz(TypedDict, total=False):
    """The voice-call leg of a send."""

    number: str
    template: str
    payload: dict[str, Any]


class CanalCarta(TypedDict, total=False):
    """The physical-letter leg of a send."""

    name: str
    modelo: str
    template: str
    variables: dict[str, Any]


class _EnvioRequestRequired(TypedDict):
    """The three fields the route always requires."""

    #: The recipient's name.
    nameTo: str
    subject: str
    #: HTML content.
    content: str


class EnvioRequest(_EnvioRequestRequired, total=False):
    """What ``legacy.send()`` takes.

    Despite the path saying e-mail, this is the multichannel request: each
    optional block adds a channel to the same notification.

    Only the enumerable is typed strictly -- ``typeSend`` is a ``Literal``.
    Business rules (``to`` required when the send is e-mail only, number
    formats, template existence) stay on the server, where they already live.
    A duplicated rule drifts, and the client's copy is the one that lies.
    """

    #: The recipient's e-mail. The server requires it when the send is e-mail only.
    to: str
    #: Your own reference, echoed back by the status routes.
    customID: str
    attachments: list[Anexo]
    validation: EnvioValidation
    sms: CanalSms
    whatsapp: CanalWhatsapp
    voz: CanalVoz
    carta: CanalCarta


class EnvioResponse(TypedDict):
    """What a send answers.

    Processing is asynchronous: the ``idEmail`` is the one handle for every
    later question -- status of any channel, proofs, the works.
    """

    idEmail: str
