"""The shapes /v3 answers.

They are ``TypedDict``s, not dataclasses: what comes back is the parsed JSON,
typed, with the field names the API uses. No conversion layer sits in the
middle -- one that could drift from the server without anyone noticing -- and
a field added to the API keeps flowing through instead of raising here.
"""

from aronline.models.allowlist_entry import AllowlistEntry
from aronline.models.channel import CHANNELS, Channel
from aronline.models.freshness import BehindTable, Freshness
from aronline.models.tag import Tag
from aronline.models.template import Template, TemplateVariable
from aronline.models.version import Version

__all__ = [
    "CHANNELS",
    "AllowlistEntry",
    "BehindTable",
    "Channel",
    "Freshness",
    "Tag",
    "Template",
    "TemplateVariable",
    "Version",
]
