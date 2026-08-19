"""One resource per family of legacy routes."""

from aronline.legacy.resources.base import LegacyResource
from aronline.legacy.resources.status import LegacyStatusResource
from aronline.legacy.resources.templates import LegacyTemplatesResource

__all__ = ["LegacyResource", "LegacyStatusResource", "LegacyTemplatesResource"]
