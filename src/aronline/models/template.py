"""A message template."""

from __future__ import annotations

from typing import TypedDict

__all__ = ["Template", "TemplateVariable"]


class TemplateVariable(TypedDict):
    """A placeholder a template expects to be filled in."""

    name: str
    #: Where the provider puts it. ``None`` when the channel has no components.
    component: str | None
    type: str | None


class Template(TypedDict):
    """A message template."""

    #: The public UUID. The internal id never leaves the API.
    id: str
    name: str
    channel: str
    #: Only channels that carry a subject fill this in.
    subject: str | None
    body: str
    active: bool
    provider_identifier: str | None
    #: A flat list -- the provider's component nesting stays in the mirror.
    variables: list[TemplateVariable]
    #: ISO 8601 with the real offset, e.g. ``2024-10-12T14:11:13-03:00``.
    created_at: str
    updated_at: str | None
