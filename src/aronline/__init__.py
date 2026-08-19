"""Official SDK for the AR Online API.

The SDK speaks the /v3 surface only. The /v1 and /v2 mirrors answer the old
contracts byte for byte -- idiosyncrasies included -- and a typed client that
"improved" them would break the callers they exist to keep working.
"""

from aronline.client import Client
from aronline.errors import ApiError, ErrorDetail
from aronline.http.transport import DEFAULT_BASE_URL, DEFAULT_TIMEOUT
from aronline.models import (
    CHANNELS,
    AllowlistEntry,
    Channel,
    Freshness,
    Tag,
    Template,
    TemplateVariable,
    Version,
)

#: This package's version -- the same string ``pyproject.toml`` carries.
VERSION = "0.1.0"

__all__ = [
    "CHANNELS",
    "DEFAULT_BASE_URL",
    "DEFAULT_TIMEOUT",
    "VERSION",
    "AllowlistEntry",
    "ApiError",
    "Channel",
    "Client",
    "ErrorDetail",
    "Freshness",
    "Tag",
    "Template",
    "TemplateVariable",
    "Version",
]
