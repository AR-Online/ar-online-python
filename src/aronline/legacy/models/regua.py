"""What the notification ladder answers when you end it."""

from __future__ import annotations

from typing import TypedDict

__all__ = ["FinalizarReguaResult"]


class FinalizarReguaResult(TypedDict, total=False):
    """What ``legacy.finalizar_regua()`` answers -- a sentence, when it answers one."""

    message: str
