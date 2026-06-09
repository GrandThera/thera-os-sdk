from __future__ import annotations

import json
from io import BytesIO

import httpx
import pytest

from thera_os import TheraOSAPIError, TheraOSClient


def make_client(handler):
    transport = httpx.MockTransport(handler)
    http = httpx.Client(transport=transport)
    return TheraOSClient(base_url="https://example.com/api/v1", client=http)


def test_forecast_run_posts_expected_payload():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["payload"] = json.loads(request.content)
        return httpx.Response(200, json={"steps": 2, "terminal_summary": {"p50": 1.2}})

    client = make_client(handler)
    result = client.forecast_run(series=[1.0, None, 1.2], steps=2, simulations=20)

    assert seen["url"] == "https://example.com/api/v1/forecast/run"
    assert seen["payload"]["series"] == [1.0, None, 1.2]
    assert result["steps"] == 2


def test_symbolic_upload_sends_multipart_form():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        body = request.content.decode()
        seen["url"] = str(request.url)
        seen["content_type"] = request.headers["content-type"]
        seen["body"] = body
        return httpx.Response(
            200,
            json={
                "rows": [],
                "columns": [],
                "numeric_columns": [],
                "dependent": "y",
                "independents": ["x"],
                "profiles": {},
            },
        )

    client = make_client(handler)
    result = client.symbolic_upload(
        BytesIO(b"x,y\n1,2\n"),
        filename="dataset.csv",
        dependent="y",
        independents=["x"],
    )

    assert seen["url"] == "https://example.com/api/v1/symbolic/upload"
    assert "multipart/form-data" in seen["content_type"]
    assert 'name="dependent"' in seen["body"]
    assert "dataset.csv" in seen["body"]
    assert result["dependent"] == "y"


def test_api_error_extracts_backend_detail():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            400,
            json={"detail": {"code": "invalid_input", "message": "Bad series"}},
        )

    client = make_client(handler)

    with pytest.raises(TheraOSAPIError) as exc_info:
        client.forecast_run(series=[])

    assert exc_info.value.status_code == 400
    assert exc_info.value.code == "invalid_input"
    assert exc_info.value.message == "Bad series"
