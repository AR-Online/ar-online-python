"""A label. Labels belong to a person, not to an entity."""

from __future__ import annotations

from typing import TypedDict

__all__ = ["Tag"]


class Tag(TypedDict):
    """A label."""

    id: str
    name: str
    color: str | None
    created_at: str
