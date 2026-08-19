"""A template as the legacy gateway shapes it."""

from __future__ import annotations

from typing import Any, Literal, TypedDict

__all__ = [
    "GW_TEMPLATE_TYPES",
    "GwTemplate",
    "GwTemplateType",
    "GwTemplateWriteResult",
    "UpdateGwTemplate",
]

#: The legacy type codes ``templates.list(type=…)`` accepts: ``"1"`` WhatsApp,
#: ``"2"`` e-mail, ``"3"`` SMS, ``"4"`` carta.
GwTemplateType = Literal["1", "2", "3", "4"]

#: The same list at runtime, for anyone validating before calling.
#:
#: An unknown code answers an **empty list, not an error** -- if you expect
#: results and get ``[]``, check the code first. Typing the union moves that
#: mistake to the type checker for whoever runs one.
GW_TEMPLATE_TYPES: tuple[GwTemplateType, ...] = ("1", "2", "3", "4")


class GwTemplate(TypedDict):
    """A template as the legacy gateway shapes it."""

    #: The public UUID.
    id: str
    #: The provider's identifier, e.g. ``hx_boleto_01``.
    templateId: str | None
    nome: str
    #: The channel as a word: ``whatsapp``, ``email``, ``sms``, ``carta``.
    tipo: str
    conteudo: str
    variaveis: list[dict[str, Any]] | None
    #: Always ``None`` -- the legacy column was 100% null. Do not build logic on it.
    metadata: None
    ativo: bool
    #: Always ``1`` -- template versioning never shipped. Do not build logic on it.
    versao: int
    #: Looks ISO with a ``Z``, but the ``Z`` is not really UTC -- see the API
    #: documentation's concepts page.
    criadoEm: str
    atualizadoEm: str | None
    #: Always ``None`` -- the legacy column was 100% null.
    criadoPor: None


class UpdateGwTemplate(TypedDict, total=False):
    """What ``templates.update()`` changes -- the two fields the gateway lets
    you edit. A key left out is a field left alone."""

    nome: str
    compartilhadoComEntidade: bool


#: What the write routes answer, passed through untyped.
#:
#: Production has not been fixtured for the writes yet, so the SDK hands the
#: object over as it came rather than promise fields it has never seen. The
#: type tightens when the mirror proves the shape.
GwTemplateWriteResult = dict[str, Any]
