"""Which version of the API is running."""

from __future__ import annotations

from typing import cast

from aronline.models.version import Version
from aronline.resources.base import Resource

__all__ = ["VersionResource"]


class VersionResource(Resource):
    """The only open route in the SDK.

    It sends no token and works on a client built without one. It is the first
    thing support asks for.
    """

    def get(self) -> Version:
        """The running version, the migration it needs and the environment."""
        # No envelope, and no credential.
        return cast("Version", self._transport.bare("/v3/version", authenticated=False))
