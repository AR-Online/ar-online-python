"""The gateway's template routes."""

from __future__ import annotations

import urllib.parse
from typing import cast

from aronline.legacy.models.gw_template import (
    GwTemplate,
    GwTemplateType,
    GwTemplateWriteResult,
    UpdateGwTemplate,
)
from aronline.legacy.resources.base import LegacyResource

__all__ = ["LegacyTemplatesResource"]


class LegacyTemplatesResource(LegacyResource):
    """The gateway's template routes.

    The whole family answers through the ``{"data": …, "statusCode": …}``
    envelope with HTTP 200 even on error; the transport unwraps it and turns the
    inner 403/404/500 into a ``LegacyApiError``, so none of that reaches you.

    The /v3 equivalent for the reads is ``client.templates`` -- same database
    row, clean contract. The writes have no /v3 equivalent yet.

    The version routes (``/versions`` and ``/versions/{v}``) are deliberately
    absent: production answers empty or 404 for every template, and a function
    that never finds anything only invites integration against a dead resource.
    """

    def list(self, *, type: GwTemplateType | None = None) -> list[GwTemplate]:
        """Your entity's templates and the ones shared with it, newest first.

        ``type`` is the legacy code -- ``"1"`` WhatsApp, ``"2"`` e-mail,
        ``"3"`` SMS, ``"4"`` carta. A code outside the four answers an **empty
        list, not an error**, which is why the type is a ``Literal``.
        """
        return cast(
            "list[GwTemplate]",
            self._transport.gw_envelope("GET", "/gw/templates", query={"type": type}),
        )

    def get(self, template_id: str) -> GwTemplate:
        """One template by its public UUID.

        Someone else's answers the family's 403 -- inside the envelope, with
        HTTP 200 on the wire.
        """
        return cast("GwTemplate", self._transport.gw_envelope("GET", _path(template_id)))

    def update(self, template_id: str, changes: UpdateGwTemplate) -> GwTemplateWriteResult:
        """Edits name and entity-wide sharing -- the two things the gateway lets
        you touch."""
        return cast(
            "GwTemplateWriteResult",
            self._transport.gw_envelope("PUT", _path(template_id), body=changes),
        )

    def deactivate(self, template_id: str) -> GwTemplateWriteResult:
        """Soft delete: the template deactivates, the row stays."""
        return cast(
            "GwTemplateWriteResult", self._transport.gw_envelope("DELETE", _path(template_id))
        )

    def set_status(self, template_id: str, *, ativo: bool) -> GwTemplateWriteResult:
        """Turns a template on or off without deleting anything."""
        return cast(
            "GwTemplateWriteResult",
            self._transport.gw_envelope(
                "PATCH", f"{_path(template_id)}/status", body={"ativo": ativo}
            ),
        )


def _path(template_id: str) -> str:
    return f"/gw/templates/{urllib.parse.quote(template_id, safe='')}"
