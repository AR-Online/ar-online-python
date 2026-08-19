"""The legacy gateway surface -- today's contract, idiosyncrasies included.

The /v3 resources at the top of the package are the clean contract. This area
speaks the old gateway exactly as its public documentation describes it, so an
integration written against the old API gets typed calls today; when a /v3
equivalent lands, the legacy function swaps transport without changing its
signature.

The names here follow the **legacy vocabulary** -- ``laudo``, ``regua``,
``voz``, ``carta``, ``EnvioRequest``. It is a deliberate exception to the
project's English rule: translating them would create a vocabulary that exists
in no documentation anywhere. Only the case convention is adapted to Python.
"""

from aronline.legacy.area import LegacyArea
from aronline.legacy.errors import LegacyApiError
from aronline.legacy.resources import (
    LegacyResource,
    LegacyStatusResource,
    LegacyTemplatesResource,
)
from aronline.legacy.transport import DEFAULT_LEGACY_BASE_URL, LegacyTransport

__all__ = [
    "DEFAULT_LEGACY_BASE_URL",
    "LegacyApiError",
    "LegacyArea",
    "LegacyResource",
    "LegacyStatusResource",
    "LegacyTemplatesResource",
    "LegacyTransport",
]
