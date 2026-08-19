"""One resource per family of routes."""

from aronline.resources.allowlist import AllowlistResource
from aronline.resources.base import Resource
from aronline.resources.freshness import FreshnessResource
from aronline.resources.tags import TagsResource
from aronline.resources.templates import TemplatesResource
from aronline.resources.version import VersionResource

__all__ = [
    "AllowlistResource",
    "FreshnessResource",
    "Resource",
    "TagsResource",
    "TemplatesResource",
    "VersionResource",
]
