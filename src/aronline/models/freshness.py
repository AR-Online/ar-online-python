"""How fresh the copy of the data is."""

from __future__ import annotations

from typing import TypedDict

__all__ = ["Freshness"]


class Freshness(TypedDict):
    """How far behind the copy is, measured by the database clock.

    It answers in COUNTS, not in a list of tables: "46 tracked, 3 behind" is an
    answer to "is it fresh"; forty-six table names is a report nobody reads at
    the moment the question is asked.
    """

    refreshed_at: str | None
    last_load_at: str | None
    #: ``None`` when no source carries a read mark yet -- which is not zero lag.
    worst_lag_seconds: int | None
    sources_tracked: int
    sources_behind: int
    #: Never loaded is its own count: it is not lag, and the fix is another.
    sources_not_loaded: int
