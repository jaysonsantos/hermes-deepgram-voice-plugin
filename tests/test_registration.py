from __future__ import annotations

from hermes_deepgram_voice import register
from hermes_deepgram_voice.stt import DeepgramSTTProvider
from hermes_deepgram_voice.tts import DeepgramTTSProvider


class Context:
    def __init__(self):
        self.tts = []
        self.stt = []

    def register_tts_provider(self, provider):
        self.tts.append(provider)

    def register_transcription_provider(self, provider):
        self.stt.append(provider)


def test_registers_both_provider_interfaces():
    ctx = Context()
    register(ctx)
    assert len(ctx.tts) == 1
    assert isinstance(ctx.tts[0], DeepgramTTSProvider)
    assert len(ctx.stt) == 1
    assert isinstance(ctx.stt[0], DeepgramSTTProvider)


def test_old_hermes_without_stt_hook_still_registers_tts():
    class OldContext:
        def __init__(self):
            self.tts = []

        def register_tts_provider(self, provider):
            self.tts.append(provider)

    ctx = OldContext()
    register(ctx)
    assert len(ctx.tts) == 1
