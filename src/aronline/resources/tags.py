"""Your labels."""

from __future__ import annotations

import urllib.parse
from typing import cast

from aronline.models.tag import Tag
from aronline.resources.base import Resource

__all__ = ["TagsResource"]


class TagsResource(Resource):
    """Labels are personal: these routes answer a PERSON's token.

    An integration token gets 403 saying so, rather than an empty list --
    which would read as "you have none".
    """

    def list(self) -> list[Tag]:
        """Your labels, ordered by name."""
        return cast("list[Tag]", self._transport.envelope("/v3/tags"))

    def get(self, tag_id: str) -> Tag:
        """A label that does not exist and one that is not yours both answer 404."""
        quoted = urllib.parse.quote(tag_id, safe="")

        return cast("Tag", self._transport.envelope(f"/v3/tags/{quoted}"))
