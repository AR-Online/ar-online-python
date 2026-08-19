"""Reading a response body that claims to be JSON.

Both transports need the same distinction: "the body was not JSON" is not the
same thing as "the body was ``null``". A proxy answering HTML has to fail like
any other refusal, while a route that legitimately answers ``null`` has to keep
answering it.
"""

from __future__ import annotations

import json
from typing import Any

__all__ = ["UNPARSED", "parse_json"]


class _Unparsed:
    """Tells "the body was not JSON" apart from "the body was ``null``"."""


#: What :func:`parse_json` returns when the text is not JSON at all.
UNPARSED = _Unparsed()


def parse_json(text: str) -> Any:
    """The parsed body, or :data:`UNPARSED` when the text is not JSON."""
    try:
        return json.loads(text)
    except ValueError:
        return UNPARSED
