from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest


@dataclass
class FakeResponse:
    status_code: int = 200
    content: bytes = b"audio"
    payload: Any = None
    text: str = ""

    def json(self):
        if isinstance(self.payload, BaseException):
            raise self.payload
        return self.payload if self.payload is not None else {}


@pytest.fixture
def fake_response():
    return FakeResponse()
