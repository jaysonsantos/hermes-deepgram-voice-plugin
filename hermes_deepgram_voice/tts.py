"""Deepgram Aura text-to-speech provider."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agent.tts_provider import TTSProvider

from .config import get_env, positive_timeout, provider_config
from .http import error_detail, post

DEFAULT_MODEL = "aura-2-thalia-en"
DEFAULT_BASE_URL = "https://api.deepgram.com/v1"

_VOICES = [
    ("aura-2-thalia-en", "Thalia — clear, confident, energetic", "en", "female"),
    ("aura-2-asteria-en", "Asteria — warm, expressive", "en", "female"),
    ("aura-2-luna-en", "Luna — friendly, natural", "en", "female"),
    ("aura-2-orion-en", "Orion — approachable, professional", "en", "male"),
    ("aura-2-arcas-en", "Arcas — deep, calm", "en", "male"),
    ("aura-2-zeus-en", "Zeus — authoritative, steady", "en", "male"),
]

_FORMAT_PARAMS: dict[str, dict[str, str]] = {
    "mp3": {"encoding": "mp3"},
    "ogg": {"encoding": "opus", "container": "ogg"},
    "opus": {"encoding": "opus", "container": "ogg"},
    "wav": {"encoding": "linear16", "container": "wav"},
    "flac": {"encoding": "flac"},
}


class DeepgramTTSProvider(TTSProvider):
    """Deepgram Aura REST provider; no Deepgram SDK is required."""

    @property
    def name(self) -> str:
        return "deepgram"

    @property
    def display_name(self) -> str:
        return "Deepgram Aura"

    @property
    def voice_compatible(self) -> bool:
        return True

    def is_available(self) -> bool:
        return bool(get_env("DEEPGRAM_API_KEY"))

    def list_voices(self) -> list[dict[str, Any]]:
        return [
            {"id": voice_id, "display": display, "language": language, "gender": gender}
            for voice_id, display, language, gender in _VOICES
        ]

    def list_models(self) -> list[dict[str, Any]]:
        return [
            {"id": voice_id, "display": display, "max_text_length": 4000}
            for voice_id, display, _language, _gender in _VOICES
        ]

    def default_model(self) -> str:
        return DEFAULT_MODEL

    def default_voice(self) -> str:
        return DEFAULT_MODEL

    def get_setup_schema(self) -> dict[str, Any]:
        return {
            "name": "Deepgram Aura",
            "badge": "paid",
            "tag": "Low-latency Aura 2 speech synthesis",
            "env_vars": [
                {
                    "key": "DEEPGRAM_API_KEY",
                    "prompt": "Deepgram API key",
                    "url": "https://console.deepgram.com/",
                }
            ],
        }

    def synthesize(
        self,
        text: str,
        output_path: str,
        *,
        voice: str | None = None,
        model: str | None = None,
        speed: float | None = None,
        format: str = "mp3",
        **extra: Any,
    ) -> str:
        api_key = get_env("DEEPGRAM_API_KEY")
        if not api_key:
            raise ValueError("DEEPGRAM_API_KEY not set. Get one at https://console.deepgram.com/")
        if not text.strip():
            raise ValueError("Deepgram TTS text must not be empty")

        config = provider_config("tts")
        voice_model = str(
            voice or config.get("voice") or config.get("model") or model or DEFAULT_MODEL
        ).strip()
        base_url = str(
            config.get("base_url") or get_env("DEEPGRAM_TTS_BASE_URL") or DEFAULT_BASE_URL
        ).rstrip("/")
        timeout = positive_timeout(config.get("timeout", 60), 60)

        requested_format = str(format or Path(output_path).suffix.lstrip(".") or "mp3").lower()
        params: dict[str, Any] = {"model": voice_model}
        params.update(_FORMAT_PARAMS.get(requested_format, _FORMAT_PARAMS["mp3"]))
        for key in ("encoding", "container", "sample_rate", "bit_rate"):
            if config.get(key) not in (None, ""):
                params[key] = config[key]
        resolved_speed = speed if speed is not None else config.get("speed")
        if resolved_speed not in (None, ""):
            params["speed"] = resolved_speed

        response = post(
            url=f"{base_url}/speak",
            api_key=api_key,
            timeout=timeout,
            headers={"Content-Type": "application/json"},
            params=params,
            json={"text": text},
        )
        if response.status_code != 200:
            raise RuntimeError(
                f"Deepgram TTS API error (HTTP {response.status_code}): {error_detail(response)}"
            )
        if not response.content:
            raise RuntimeError("Deepgram TTS returned an empty audio response")

        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(response.content)
        return str(target)
