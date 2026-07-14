"""Shared Deepgram HTTP helpers."""

from __future__ import annotations

from typing import Any

import requests


def error_detail(response: requests.Response) -> str:
    """Extract a bounded, human-readable error without leaking credentials."""
    detail = (response.text or "")[:500]
    try:
        body = response.json()
    except (TypeError, ValueError):
        return detail or "empty response"
    if isinstance(body, dict):
        return str(body.get("err_msg") or body.get("message") or body.get("error") or detail)
    return detail or "empty response"


def post(*, url: str, api_key: str, timeout: float, **kwargs: Any) -> requests.Response:
    """POST to Deepgram with standard token authentication."""
    headers = dict(kwargs.pop("headers", {}))
    headers["Authorization"] = f"Token {api_key}"
    return requests.post(url, headers=headers, timeout=timeout, **kwargs)
