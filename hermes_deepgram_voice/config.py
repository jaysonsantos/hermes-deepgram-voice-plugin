"""Hermes config and credential helpers."""

from __future__ import annotations

import os
from typing import Any


def get_env(name: str, default: str = "") -> str:
    """Read process or Hermes dotenv-backed environment values."""
    try:
        from hermes_cli.config import get_env_value

        value = get_env_value(name)
    except (ImportError, RuntimeError):
        value = os.getenv(name)
    return str(value if value is not None else default).strip()


def provider_config(section: str) -> dict[str, Any]:
    """Return ``<section>.deepgram`` from Hermes config."""
    try:
        from hermes_cli.config import load_config

        config = load_config()
    except (ImportError, OSError, ValueError, TypeError):
        return {}
    root = config.get(section) if isinstance(config, dict) else None
    deepgram = root.get("deepgram") if isinstance(root, dict) else None
    return deepgram if isinstance(deepgram, dict) else {}


def positive_timeout(value: Any, default: float) -> float:
    """Coerce a timeout to a positive float."""
    try:
        timeout = float(value)
    except (TypeError, ValueError):
        return default
    return timeout if timeout > 0 else default


def bool_param(value: Any, *, default: bool) -> str:
    """Convert common config representations to an API boolean string."""
    if value is None:
        enabled = default
    elif isinstance(value, bool):
        enabled = value
    elif isinstance(value, int | float):
        enabled = bool(value)
    else:
        enabled = str(value).strip().lower() in {"1", "true", "yes", "on"}
    return "true" if enabled else "false"
