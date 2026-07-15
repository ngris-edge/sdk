"""Tests for SDK logging: redaction, request-id propagation, and the
guarantee that secret values never reach a log handler.

These tests use ``caplog`` which captures records *before* any formatter
runs, so a leaked secret would be visible in ``record.getMessage()`` —
the assertions look at the rendered message text rather than the raw
args, which is exactly the surface a misconfigured app would write to
disk.
"""

from __future__ import annotations

import logging

import httpx
import pytest
import respx

from ngris import AuthenticationError, Ngris, RateLimitError
from ngris._logging import (
    extract_request_id,
    redact_body,
    redact_headers,
    truncate_for_log,
)


class TestRedactionUnits:
    def test_header_redaction_case_insensitive(self) -> None:
        out = redact_headers(
            {
                "X-API-Key": "ngris_super_secret",
                "authorization": "Bearer abc.def.ghi",
                "Cookie": "session=xxx",
                "User-Agent": "ngris/1.0",
                "X-Request-ID": "req-123",
            }
        )
        assert out["X-API-Key"] == "***"
        assert out["authorization"] == "***"
        assert out["Cookie"] == "***"
        # Non-secret headers pass through unchanged.
        assert out["User-Agent"] == "ngris/1.0"
        assert out["X-Request-ID"] == "req-123"

    def test_body_redaction_walks_nested(self) -> None:
        body = {
            "username": "alice",
            "password": "hunter2",
            "nested": {
                "api_key": "ngris_xxx",
                "ok": True,
            },
            "items": [
                {"client_secret": "shh"},
                {"name": "fine"},
            ],
        }
        red = redact_body(body)
        assert red["username"] == "alice"
        assert red["password"] == "***"
        assert red["nested"]["api_key"] == "***"
        assert red["nested"]["ok"] is True
        assert red["items"][0]["client_secret"] == "***"
        assert red["items"][1]["name"] == "fine"

    def test_body_redaction_handles_bytes(self) -> None:
        out = redact_body({"upload": b"x" * 1000, "size": 1000})
        assert out["upload"] == "<bytes:1000>"
        assert out["size"] == 1000

    def test_truncate_for_log_caps_payload(self) -> None:
        big = {"data": "x" * 10000}
        rendered = truncate_for_log(big)
        # 4KB cap + a "...<+Nb>" suffix.
        assert len(rendered) <= 4096 + 32
        assert "...<+" in rendered

    def test_extract_request_id_either_header(self) -> None:
        assert extract_request_id({"X-Request-ID": "abc"}) == "abc"
        assert extract_request_id({"x-correlation-id": "xyz"}) == "xyz"
        assert extract_request_id({"X-Other": "no"}) is None
        assert extract_request_id(None) is None
        assert extract_request_id({}) is None


class TestHTTPLogging:
    @respx.mock
    def test_success_logs_at_info_with_request_id(self, caplog) -> None:
        respx.get("https://api.example.test/endpoints").respond(
            200,
            json={"items": [], "total": 0, "page": 1, "page_size": 50},
            headers={"X-Request-ID": "req-aaa"},
        )

        client = Ngris(api_key="ngris_test", base_url="https://api.example.test")
        with caplog.at_level(logging.INFO, logger="ngris.http"):
            client.endpoints.list()

        msgs = [r.getMessage() for r in caplog.records]
        assert any(
            "GET /endpoints" in m and "status=200" in m and "req-aaa" in m
            for m in msgs
        ), msgs

    @respx.mock
    def test_error_response_attaches_request_id_to_exception(self) -> None:
        respx.get("https://api.example.test/endpoints/nope").respond(
            401,
            json={"error": "Invalid API key"},
            headers={"X-Request-ID": "req-fail-1"},
        )

        client = Ngris(api_key="ngris_test", base_url="https://api.example.test")
        with pytest.raises(AuthenticationError) as excinfo:
            client.endpoints.get("nope")

        err = excinfo.value
        assert err.request_id == "req-fail-1"
        # __repr__ surfaces the id so a stray print() in user code shows it.
        assert "req-fail-1" in repr(err)

    @respx.mock
    def test_debug_logs_redact_secrets(self, caplog) -> None:
        respx.post("https://api.example.test/auth/login").respond(
            200, json={"token": "tk", "user": None, "mfa_required": False}
        )

        client = Ngris(api_key="SHOULD_NOT_LEAK", base_url="https://api.example.test")
        with caplog.at_level(logging.DEBUG, logger="ngris.http"):
            client.auth.login("alice", "MY_REAL_PASSWORD")

        text = "\n".join(r.getMessage() for r in caplog.records)
        # API key from headers must never appear in plaintext log output.
        assert "SHOULD_NOT_LEAK" not in text
        # Body password must be redacted too.
        assert "MY_REAL_PASSWORD" not in text
        assert "***" in text

    @respx.mock
    def test_retry_emits_warning(self, caplog) -> None:
        respx.get("https://api.example.test/endpoints").mock(
            side_effect=[
                httpx.Response(503, json={"error": "down"}, headers={"X-Request-ID": "r1"}),
                httpx.Response(
                    200,
                    json={"items": [], "total": 0, "page": 1, "page_size": 50},
                    headers={"X-Request-ID": "r2"},
                ),
            ]
        )

        client = Ngris(
            api_key="k",
            base_url="https://api.example.test",
            max_retries=1,
            backoff_factor=0.0,  # no real sleep in tests
        )
        with caplog.at_level(logging.WARNING, logger="ngris.http"):
            client.endpoints.list()

        warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
        assert any("retrying" in r.getMessage() and "r1" in r.getMessage() for r in warnings)
