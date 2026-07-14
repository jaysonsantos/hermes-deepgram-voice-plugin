"""Deepgram Nova speech-to-text provider."""

from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Any

from agent.transcription_provider import TranscriptionProvider

from .config import bool_param, get_env, positive_timeout, provider_config
from .http import error_detail, post

DEFAULT_MODEL = "nova-3"
DEFAULT_BASE_URL = "https://api.deepgram.com/v1"


def extract_transcript(payload: dict[str, Any]) -> str:
    """Join the best alternative from every returned audio channel."""
    channels = payload.get("results", {}).get("channels", [])
    if not isinstance(channels, list):
        return ""
    transcripts: list[str] = []
    for channel in channels:
        alternatives = channel.get("alternatives", []) if isinstance(channel, dict) else []
        first = alternatives[0] if alternatives and isinstance(alternatives[0], dict) else {}
        paragraphs = first.get("paragraphs") if isinstance(first, dict) else None
        text = paragraphs.get("transcript") if isinstance(paragraphs, dict) else None
        if not isinstance(text, str) or not text.strip():
            text = first.get("transcript") if isinstance(first, dict) else None
        if isinstance(text, str) and text.strip():
            transcripts.append(text.strip())
    return " ".join(transcripts)


class DeepgramSTTProvider(TranscriptionProvider):
    """Deepgram pre-recorded Listen API provider."""

    @property
    def name(self) -> str:
        return "deepgram"

    @property
    def display_name(self) -> str:
        return "Deepgram Nova"

    def is_available(self) -> bool:
        return bool(get_env("DEEPGRAM_API_KEY"))

    def list_models(self) -> list[dict[str, Any]]:
        return [
            {"id": "nova-3", "display": "Nova 3"},
            {"id": "nova-2", "display": "Nova 2"},
            {"id": "enhanced", "display": "Enhanced"},
            {"id": "base", "display": "Base"},
        ]

    def get_setup_schema(self) -> dict[str, Any]:
        return {
            "name": "Deepgram Nova",
            "badge": "paid",
            "tag": "Fast multilingual transcription with language detection",
            "env_vars": [
                {
                    "key": "DEEPGRAM_API_KEY",
                    "prompt": "Deepgram API key",
                    "url": "https://console.deepgram.com/",
                }
            ],
        }

    def transcribe(
        self,
        file_path: str,
        *,
        model: str | None = None,
        language: str | None = None,
        **extra: Any,
    ) -> dict[str, Any]:
        api_key = get_env("DEEPGRAM_API_KEY")
        if not api_key:
            return self._error("DEEPGRAM_API_KEY not set")

        config = provider_config("stt")
        model_name = str(model or config.get("model") or DEFAULT_MODEL).strip()
        base_url = str(
            config.get("base_url") or get_env("DEEPGRAM_STT_BASE_URL") or DEFAULT_BASE_URL
        ).rstrip("/")
        timeout = positive_timeout(config.get("timeout", 120), 120)
        params: dict[str, str] = {
            "model": model_name,
            "smart_format": bool_param(config.get("smart_format"), default=True),
            "punctuate": bool_param(config.get("punctuate"), default=True),
        }
        language_name = str(language or config.get("language") or "").strip()
        if language_name:
            params["language"] = language_name
        else:
            params["detect_language"] = bool_param(config.get("detect_language"), default=True)
        for key in ("diarize", "paragraphs", "utterances", "numerals", "dictation"):
            if key in config:
                params[key] = bool_param(config[key], default=False)

        content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
        try:
            with Path(file_path).open("rb") as audio_file:
                response = post(
                    url=f"{base_url}/listen",
                    api_key=api_key,
                    timeout=timeout,
                    headers={"Content-Type": content_type},
                    params=params,
                    data=audio_file,
                )
            if response.status_code != 200:
                detail = error_detail(response)
                return self._error(
                    f"Deepgram STT API error (HTTP {response.status_code}): {detail}"
                )
            transcript = extract_transcript(response.json())
            if not transcript:
                return self._error("Deepgram STT returned an empty transcript")
            return {"success": True, "transcript": transcript, "provider": self.name}
        except (OSError, ValueError, TypeError) as exc:
            return self._error(f"Deepgram STT transcription failed: {exc}")
        except Exception as exc:
            return self._error(f"Deepgram STT transcription failed: {exc}")

    def _error(self, message: str) -> dict[str, Any]:
        return {"success": False, "transcript": "", "provider": self.name, "error": message}
