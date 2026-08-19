"""What ``legacy.sending_proof()`` gives back."""

from __future__ import annotations

from typing import TypedDict

__all__ = ["SendingProof"]


class SendingProof(TypedDict):
    """The sending proof, already decoded.

    The wire answers one of two bodies: ``{"content": …}`` with the PDF in
    base64, or ``{"message": …}`` when the e-mail has no delivery status yet.
    The SDK decodes the PDF for you and keeps the raw base64 reachable --
    exactly one of ``pdf`` and ``message`` is filled in.

    These three keys are the SDK's own shape, not the gateway's, so they are
    written the way Python writes names.
    """

    #: The proof, decoded. ``None`` while the gateway only has a message.
    pdf: bytes | None
    #: The base64 exactly as the gateway sent it.
    content_base64: str | None
    #: The gateway's sentence when the proof is not available yet -- ask again later.
    message: str | None
