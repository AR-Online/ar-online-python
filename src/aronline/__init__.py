"""Official SDK for the AR Online API.

The SDK speaks the /v3 surface only. The /v1 and /v2 mirrors answer the old
contracts byte for byte -- idiosyncrasies included -- and a typed client that
"improved" them would break the callers they exist to keep working.
"""

#: Where /v3 lives. Override it to point at staging or at a local process.
DEFAULT_BASE_URL = "https://api.aronline.com.br"

#: This package's version -- the same string ``pyproject.toml`` carries.
VERSION = "0.1.0"

__all__ = ["DEFAULT_BASE_URL", "VERSION"]
