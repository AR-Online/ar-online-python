"""How fresh the copy of the data is."""

from __future__ import annotations

from typing import TypedDict

__all__ = ["BehindTable", "Freshness"]


class BehindTable(TypedDict):
    """A table whose copy is past the threshold."""

    legacy: str
    lag_seconds: int


class Freshness(TypedDict):
    """How far behind the copy is, measured by the database clock."""

    refreshed_at: str | None
    last_load_at: str | None
    #: ``None`` when no table carries a read mark yet.
    worst_lag_seconds: int | None
    tables_tracked: int
    #: Never loaded is its own count -- it is not lag, and the fix is another.
    tables_never_loaded: int
    #: Past the threshold, worst first.
    behind: list[BehindTable]
