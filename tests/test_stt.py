from __future__ import annotations

from hermes_deepgram_voice import stt
from hermes_deepgram_voice.stt import DeepgramSTTProvider, extract_transcript


def _key(name: str, default: str = "") -> str:
    return "secret" if name == "DEEPGRAM_API_KEY" else default


def _payload(text: str = "hello") -> dict:
    return {"results": {"channels": [{"alternatives": [{"transcript": text}]}]}}


def test_transcribe_auto_detects_language(monkeypatch, tmp_path, fake_response):
    captured = {}
    audio = tmp_path / "sample.wav"
    audio.write_bytes(b"RIFFaudio")
    fake_response.payload = _payload("olá mundo")
    monkeypatch.setattr(stt, "get_env", _key)
    monkeypatch.setattr(stt, "provider_config", lambda section: {})
    monkeypatch.setattr(stt, "post", lambda **kwargs: captured.update(kwargs) or fake_response)

    result = DeepgramSTTProvider().transcribe(str(audio))

    assert result == {"success": True, "transcript": "olá mundo", "provider": "deepgram"}
    assert captured["url"] == "https://api.deepgram.com/v1/listen"
    assert captured["params"]["model"] == "nova-3"
    assert captured["params"]["detect_language"] == "true"
    assert "language" not in captured["params"]
    assert captured["headers"]["Content-Type"] == "audio/x-wav"


def test_explicit_language_and_options(monkeypatch, tmp_path, fake_response):
    captured = {}
    audio = tmp_path / "sample.ogg"
    audio.write_bytes(b"ogg")
    fake_response.payload = _payload()
    monkeypatch.setattr(stt, "get_env", _key)
    monkeypatch.setattr(
        stt,
        "provider_config",
        lambda section: {"diarize": True, "paragraphs": "yes", "timeout": "9"},
    )
    monkeypatch.setattr(stt, "post", lambda **kwargs: captured.update(kwargs) or fake_response)

    DeepgramSTTProvider().transcribe(str(audio), model="nova-2", language="de")

    assert captured["timeout"] == 9
    assert captured["params"]["model"] == "nova-2"
    assert captured["params"]["language"] == "de"
    assert "detect_language" not in captured["params"]
    assert captured["params"]["diarize"] == "true"
    assert captured["params"]["paragraphs"] == "true"


def test_http_error(monkeypatch, tmp_path, fake_response):
    audio = tmp_path / "sample.wav"
    audio.write_bytes(b"audio")
    fake_response.status_code = 429
    fake_response.payload = {"message": "rate limited"}
    monkeypatch.setattr(stt, "get_env", _key)
    monkeypatch.setattr(stt, "provider_config", lambda section: {})
    monkeypatch.setattr(stt, "post", lambda **kwargs: fake_response)
    result = DeepgramSTTProvider().transcribe(str(audio))
    assert result["success"] is False
    assert "HTTP 429" in result["error"]
    assert "rate limited" in result["error"]


def test_missing_key(monkeypatch, tmp_path):
    monkeypatch.setattr(stt, "get_env", lambda name, default="": default)
    result = DeepgramSTTProvider().transcribe(str(tmp_path / "missing.wav"))
    assert result == {
        "success": False,
        "transcript": "",
        "provider": "deepgram",
        "error": "DEEPGRAM_API_KEY not set",
    }


def test_empty_transcript(monkeypatch, tmp_path, fake_response):
    audio = tmp_path / "sample.wav"
    audio.write_bytes(b"audio")
    fake_response.payload = _payload("")
    monkeypatch.setattr(stt, "get_env", _key)
    monkeypatch.setattr(stt, "provider_config", lambda section: {})
    monkeypatch.setattr(stt, "post", lambda **kwargs: fake_response)
    result = DeepgramSTTProvider().transcribe(str(audio))
    assert not result["success"]
    assert "empty transcript" in result["error"]


def test_extract_transcript_joins_channels_and_prefers_paragraphs():
    payload = {
        "results": {
            "channels": [
                {"alternatives": [{"transcript": "fallback", "paragraphs": {"transcript": "one"}}]},
                {"alternatives": [{"transcript": "two"}]},
            ]
        }
    }
    assert extract_transcript(payload) == "one two"
    assert extract_transcript({}) == ""


def test_provider_metadata(monkeypatch):
    monkeypatch.setattr(stt, "get_env", _key)
    provider = DeepgramSTTProvider()
    assert provider.name == "deepgram"
    assert provider.is_available()
    assert provider.default_model() == "nova-3"
    assert provider.get_setup_schema()["env_vars"][0]["key"] == "DEEPGRAM_API_KEY"
