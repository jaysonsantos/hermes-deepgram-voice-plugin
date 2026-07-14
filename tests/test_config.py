from __future__ import annotations

import pytest

from hermes_deepgram_voice import config
from hermes_deepgram_voice.config import bool_param, positive_timeout


@pytest.mark.parametrize(
    ("value", "default", "expected"),
    [
        (None, True, "true"),
        (None, False, "false"),
        (True, False, "true"),
        (0, True, "false"),
        ("yes", False, "true"),
        ("off", True, "false"),
    ],
)
def test_bool_param(value, default, expected):
    assert bool_param(value, default=default) == expected


@pytest.mark.parametrize(("value", "expected"), [("2.5", 2.5), (0, 10), (-1, 10), ("x", 10)])
def test_positive_timeout(value, expected):
    assert positive_timeout(value, 10) == expected


def test_get_env_uses_hermes_dotenv_lookup(monkeypatch):
    import hermes_cli.config

    monkeypatch.setattr(hermes_cli.config, "get_env_value", lambda name: "  from-dotenv  ")
    assert config.get_env("DEEPGRAM_API_KEY") == "from-dotenv"


def test_provider_config_reads_only_mapping(monkeypatch):
    import hermes_cli.config

    monkeypatch.setattr(
        hermes_cli.config,
        "load_config",
        lambda: {"tts": {"deepgram": {"timeout": 42}}},
    )
    assert config.provider_config("tts") == {"timeout": 42}
    assert config.provider_config("stt") == {}


def test_provider_config_handles_loader_failure(monkeypatch):
    import hermes_cli.config

    def fail():
        raise OSError("broken config")

    monkeypatch.setattr(hermes_cli.config, "load_config", fail)
    assert config.provider_config("tts") == {}
