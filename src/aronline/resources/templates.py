"""The message templates your identity reaches."""

from __future__ import annotations

import urllib.parse
from typing import cast

from aronline.models.channel import Channel
from aronline.models.template import Template
from aronline.resources.base import Resource

__all__ = ["TemplatesResource"]


class TemplatesResource(Resource):
    """Message templates."""

    def list(self, *, channel: Channel | None = None) -> list[Template]:
        """The templates you reach, newest first.

        Unlike the ``/gw/templates`` mirror, it does not filter by lineage: a
        template created in /v3 has no legacy row and still shows up.
        """
        return cast(
            "list[Template]",
            self._transport.envelope("/v3/templates", query={"channel": channel}),
        )

    def get(self, template_id: str) -> Template:
        """One template by its public UUID.

        A template that does not exist and one that is not yours fail the same
        way -- 404. Answering 403 would confirm the id exists.
        """
        quoted = urllib.parse.quote(template_id, safe="")

        return cast("Template", self._transport.envelope(f"/v3/templates/{quoted}"))
