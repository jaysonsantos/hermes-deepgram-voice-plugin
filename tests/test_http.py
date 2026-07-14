from __future__ import annotations

from hermes_deepgram_voice import http


def test_post_adds_token_auth(monkeypatch, fake_response):
    captured = {}
    monkeypatch.setattr(
        http.requests,
        "post",
        lambda url, **kwargs: captured.update({"url": url, **kwargs}) or fake_response,
    )
    assert (
        http.post(
            url="https://api.deepgram.com/v1/speak",
            api_key="secret",
            timeout=3,
            headers={"Content-Type": "application/json"},
            json={"text": "hi"},
        )
        is fake_response
    )
    assert captured["headers"]["Authorization"] == "Token secret"
    assert captured["headers"]["Content-Type"] == "application/json"
    assert captured["timeout"] == 3


def test_error_detail_handles_non_json(fake_response):
    fake_response.text = "plain failure"
    fake_response.payload = ValueError("not json")
    assert http.error_detail(fake_response) == "plain failure"


def test_error_detail_handles_non_mapping_json(fake_response):
    fake_response.payload = ["unexpected"]
    assert http.error_detail(fake_response) == "empty response"
