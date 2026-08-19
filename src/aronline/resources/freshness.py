"""How far behind the copy of the data is."""

from __future__ import annotations

from typing import cast

from aronline.models.freshness import Freshness
from aronline.resources.base import Resource

__all__ = ["FreshnessResource"]


class FreshnessResource(Resource):
    """The freshness of the copy.

    It answers the practical question behind a query that returned less than
    expected: is the API wrong, or is the load late? Without this number the
    two look the same.
    """

    def get(self) -> Freshness:
        """Measured by the database clock, not by the caller's."""
        # No envelope on this one: the route answers the object itself.
        return cast("Freshness", self._transport.bare("/v3/freshness"))
