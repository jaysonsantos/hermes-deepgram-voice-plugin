"""Deepgram voice providers for Hermes Agent."""

from __future__ import annotations

import logging

from .stt import DeepgramSTTProvider
from .tts import DeepgramTTSProvider

logger = logging.getLogger(__name__)


def register(ctx) -> None:
    """Register TTS and STT providers with the available Hermes plugin API."""
    ctx.register_tts_provider(DeepgramTTSProvider())
    register_stt = getattr(ctx, "register_transcription_provider", None)
    if callable(register_stt):
        register_stt(DeepgramSTTProvider())
    else:
        logger.info("Hermes does not expose the STT plugin hook; Deepgram TTS remains available")


__all__ = ["DeepgramSTTProvider", "DeepgramTTSProvider", "register"]
