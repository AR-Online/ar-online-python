"""What the API is running."""

from __future__ import annotations

from typing import TypedDict

__all__ = ["Version"]


class Version(TypedDict):
    """The running version, the migration it needs and the environment."""

    version: str
    min_migration: str
    environment: str
