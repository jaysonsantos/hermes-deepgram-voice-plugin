from __future__ import annotations

import pytest

from hermes_deepgram_voice import tts
from hermes_deepgram_voice.tts import DeepgramTTSProvider


def _key(name: str, default: str = "") -> str:
    return "secret" if name == "DEEPGRAM_API_KEY" else default


def test_synthesize_mp3(monkeypatch, tmp_path, fake_response):
    captured = {}
    monkeypatch.setattr(tts, "get_env", _key)
    monkeypatch.setattr(tts, "provider_config", lambda section: {})

    def fake_post(**kwargs):
        captured.update(kwargs)
        return fake_response

    monkeypatch.setattr(tts, "post", fake_post)
    output = tmp_path / "voice.mp3"

    result = DeepgramTTSProvider().synthesize("hello", str(output))

    assert result == str(output)
    assert output.read_bytes() == b"audio"
    assert captured["url"] == "https://api.deepgram.com/v1/speak"
    assert captured["api_key"] == "secret"
    assert captured["json"] == {"text": "hello"}
    assert captured["params"] == {"model": "aura-2-thalia-en", "encoding": "mp3"}


def test_voice_and_ogg_options(monkeypatch, tmp_path, fake_response):
    captured = {}
    monkeypatch.setattr(tts, "get_env", _key)
    monkeypatch.setattr(
        tts,
        "provider_config",
        lambda section: {"sample_rate": 48000, "timeout": 7, "speed": 1.1},
    )
    monkeypatch.setattr(tts, "post", lambda **kwargs: captured.update(kwargs) or fake_response)

    DeepgramTTSProvider().synthesize(
        "olá", str(tmp_path / "voice.ogg"), voice="aura-2-luna-en", format="ogg"
    )

    assert captured["timeout"] == 7
    assert captured["params"] == {
        "model": "aura-2-luna-en",
        "encoding": "opus",
        "container": "ogg",
        "sample_rate": 48000,
        "speed": 1.1,
    }


def test_call_speed_overrides_config(monkeypatch, tmp_path, fake_response):
    captured = {}
    monkeypatch.setattr(tts, "get_env", _key)
    monkeypatch.setattr(tts, "provider_config", lambda section: {"speed": 0.9})
    monkeypatch.setattr(tts, "post", lambda **kwargs: captured.update(kwargs) or fake_response)
    DeepgramTTSProvider().synthesize("hi", str(tmp_path / "x.wav"), speed=1.25, format="wav")
    assert captured["params"]["speed"] == 1.25
    assert captured["params"]["encoding"] == "linear16"
    assert captured["params"]["container"] == "wav"


def test_missing_key(monkeypatch, tmp_path):
    monkeypatch.setattr(tts, "get_env", lambda name, default="": default)
    with pytest.raises(ValueError, match="DEEPGRAM_API_KEY"):
        DeepgramTTSProvider().synthesize("hello", str(tmp_path / "x.mp3"))


def test_api_error_is_bounded(monkeypatch, tmp_path, fake_response):
    monkeypatch.setattr(tts, "get_env", _key)
    monkeypatch.setattr(tts, "provider_config", lambda section: {})
    fake_response.status_code = 401
    fake_response.payload = {"err_msg": "invalid credentials"}
    monkeypatch.setattr(tts, "post", lambda **kwargs: fake_response)
    with pytest.raises(RuntimeError, match="HTTP 401.*invalid credentials"):
        DeepgramTTSProvider().synthesize("hello", str(tmp_path / "x.mp3"))


def test_empty_audio_rejected(monkeypatch, tmp_path, fake_response):
    monkeypatch.setattr(tts, "get_env", _key)
    monkeypatch.setattr(tts, "provider_config", lambda section: {})
    fake_response.content = b""
    monkeypatch.setattr(tts, "post", lambda **kwargs: fake_response)
    with pytest.raises(RuntimeError, match="empty audio"):
        DeepgramTTSProvider().synthesize("hello", str(tmp_path / "x.mp3"))


def test_provider_metadata(monkeypatch):
    monkeypatch.setattr(tts, "get_env", _key)
    provider = DeepgramTTSProvider()
    assert provider.name == "deepgram"
    assert provider.is_available()
    assert provider.voice_compatible
    assert provider.default_voice() == "aura-2-thalia-en"
    assert any(v["id"] == "aura-2-thalia-en" for v in provider.list_voices())
    assert provider.get_setup_schema()["env_vars"][0]["key"] == "DEEPGRAM_API_KEY"
