"""A recipient allowed to receive messages."""

from __future__ import annotations

from typing import TypedDict

__all__ = ["AllowlistEntry"]


class AllowlistEntry(TypedDict):
    """An allowed recipient."""

    id: str
    recipient: str
    created_at: str
