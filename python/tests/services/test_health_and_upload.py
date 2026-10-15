"""``endpoints.get_health`` and ``templates.upload`` against the real api-server contract.

- ``GET /endpoints/{uuid}/health`` (api-server ``UserGetEndpointHealth``)
  answers ``endpointHealthResponse``: ``endpoint_uuid`` (+ the deprecated
  ``endpoint_id``), ``has_active_agent``, ``uptime_24h`` / ``uptime_7d`` /
  ``uptime_30d``, ``avg_latency_ms``, ``last_check`` (null before the first
  probe) and ``recent_checks``. A probe served from the status cache has
  ``id`` 0 and can carry the zero time.
- ``POST /templates`` (api-server ``UserUploadCustomTemplateHandler``) reads a
  multipart form: ``type``, the page as the ``template`` file part, and
  ``active=true``. It answers 201 with the stored template.
"""

from __future__ import annotations

import email.policy
from datetime import datetime, timezone
from email.message import Message
from email.parser import BytesParser

import httpx
import pytest
import respx

from ngris import AsyncNgris, Ngris
from ngris.models import CustomTemplate, HealthCheck, HealthStatus

BASE = "https://api.example.test"
EP = "019bb1e4-e785-77d2-9966-c3cff31d0a0e"
TEMPLATE = "019c0d1f-6a2b-7c3d-8e4f-5a6b7c8d9e0f"
USER = "019a0000-1111-7222-8333-444455556666"


@pytest.fixture
def client() -> Ngris:
    with Ngris(api_key="ngris_test", base_url=BASE, max_retries=0, http2=False) as c:
        yield c


def _health(**over: object) -> dict[str, object]:
    body: dict[str, object] = {
        "endpoint_id": 42,
        "endpoint_uuid": EP,
        "has_active_agent": True,
        "uptime_24h": 99.31,
        "uptime_7d": 99.9,
        "uptime_30d": 100,
        "avg_latency_ms": 41.25,
        "last_check": {
            "id": 9001,
            "status": "healthy",
            "status_code": 200,
            "latency_ms": 38,
            "error_message": None,
            "checked_at": "2026-10-15T09:12:03Z",
        },
        "recent_checks": [
            {
                "id": 9001,
                "status": "healthy",
                "status_code": 200,
                "latency_ms": 38,
                "error_message": None,
                "checked_at": "2026-10-15T09:12:03Z",
            },
            {
                "id": 9000,
                "status": "unhealthy",
                "status_code": None,
                "latency_ms": None,
                "error_message": "dial tcp 10.0.0.5:8080: i/o timeout",
                "checked_at": "2026-10-15T09:11:03Z",
            },
        ],
    }
    body.update(over)
    return body


class TestGetHealth:
    @respx.mock
    def test_parses_the_real_health_response(self, client: Ngris) -> None:
        route = respx.get(f"{BASE}/endpoints/{EP}/health").respond(200, json=_health())

        health = client.endpoints.get_health(EP)

        assert route.called
        assert isinstance(health, HealthStatus)
        assert health.endpoint_uuid == EP
        assert health.has_active_agent is True
        assert (health.uptime_24h, health.uptime_7d, health.uptime_30d) == (99.31, 99.9, 100.0)
        assert health.avg_latency_ms == 41.25
        assert isinstance(health.last_check, HealthCheck)
        assert health.last_check.status == "healthy"
        assert health.last_check.status_code == 200
        assert health.last_check.latency_ms == 38
        assert health.last_check.checked_at == datetime(2026, 10, 15, 9, 12, 3, tzinfo=timezone.utc)
        assert [c.status for c in health.recent_checks] == ["healthy", "unhealthy"]
        failed = health.recent_checks[1]
        assert failed.status_code is None and failed.latency_ms is None
        assert failed.error_message == "dial tcp 10.0.0.5:8080: i/o timeout"

    @respx.mock
    def test_no_probe_yet(self, client: Ngris) -> None:
        respx.get(f"{BASE}/endpoints/{EP}/health").respond(
            200,
            json=_health(
                has_active_agent=False,
                uptime_24h=0,
                uptime_7d=0,
                uptime_30d=0,
                avg_latency_ms=0,
                last_check=None,
                recent_checks=[],
            ),
        )

        health = client.endpoints.get_health(EP)

        assert health.last_check is None
        assert health.recent_checks == []
        assert health.uptime_30d == 0.0

    @respx.mock
    def test_cached_latest_probe_and_post_sunset_shape(self, client: Ngris) -> None:
        # The latest probe from the status cache has no row id (0) and, without
        # a cached timestamp, Go's zero time. After the integer-id sunset the
        # response has no endpoint_id.
        body = _health(
            last_check={
                "id": 0,
                "status": "unhealthy",
                "status_code": 502,
                "latency_ms": 12,
                "error_message": "bad gateway",
                "checked_at": "0001-01-01T00:00:00Z",
            }
        )
        del body["endpoint_id"]
        respx.get(f"{BASE}/endpoints/{EP}/health").respond(200, json=body)

        health = client.endpoints.get_health(EP)

        assert health.endpoint_id is None
        assert health.endpoint_uuid == EP
        assert health.last_check is not None
        assert health.last_check.id == 0
        assert health.last_check.status_code == 502
        assert health.last_check.checked_at.year == 1

    @respx.mock
    async def test_async(self) -> None:
        respx.get(f"{BASE}/endpoints/{EP}/health").respond(200, json=_health())
        async with AsyncNgris(api_key="ngris_test", base_url=BASE, max_retries=0, http2=False) as c:
            health = await c.endpoints.get_health(EP)
        assert health.has_active_agent is True
        assert len(health.recent_checks) == 2


def _stored_template(**over: object) -> dict[str, object]:
    # The upload handler encodes the inserted row: its created_at/updated_at
    # are not read back, so they are Go's zero time.
    body: dict[str, object] = {
        "id": 7,
        "uuid": TEMPLATE,
        "user_id": 3,
        "user_uuid": USER,
        "type": "not_found",
        "content": "<h1>Gone</h1>",
        "is_active": True,
        "created_at": "0001-01-01T00:00:00Z",
        "updated_at": "0001-01-01T00:00:00Z",
    }
    body.update(over)
    return body


def _multipart(request: httpx.Request) -> dict[str, Message]:
    """Parse a multipart/form-data request body into {field name: part}."""
    content_type = request.headers["content-type"]
    raw = b"Content-Type: " + content_type.encode() + b"\r\n\r\n" + request.content
    message = BytesParser(policy=email.policy.HTTP).parsebytes(raw)
    assert message.is_multipart()
    parts: dict[str, Message] = {}
    for part in message.iter_parts():
        name = part.get_param("name", header="content-disposition")
        assert isinstance(name, str)
        parts[name] = part
    return parts


class TestTemplateUpload:
    @respx.mock
    def test_sends_the_multipart_form_the_handler_reads(self, client: Ngris) -> None:
        route = respx.post(f"{BASE}/templates").respond(201, json=_stored_template())

        tpl = client.templates.upload("not_found", "<h1>Gone</h1>", active=True)

        request = route.calls.last.request
        assert request.headers["content-type"].startswith("multipart/form-data; boundary=")
        assert request.headers["x-api-key"] == "ngris_test"
        parts = _multipart(request)
        assert set(parts) == {"type", "active", "template"}
        assert parts["type"].get_payload(decode=True) == b"not_found"
        assert parts["active"].get_payload(decode=True) == b"true"
        page = parts["template"]
        assert page.get_filename() == "template.html"
        assert page.get_content_type() == "text/html"
        assert page.get_payload(decode=True) == b"<h1>Gone</h1>"

        assert isinstance(tpl, CustomTemplate)
        assert tpl.uuid == TEMPLATE
        assert tpl.type == "not_found"
        assert tpl.is_active is True

    @respx.mock
    def test_inactive_by_default_and_bytes_content(self, client: Ngris) -> None:
        route = respx.post(f"{BASE}/templates").respond(201, json=_stored_template(is_active=False))
        page = "<p>Ralenti — réessayez</p>".encode()

        tpl = client.templates.upload("rate_limit", page)

        parts = _multipart(route.calls.last.request)
        assert set(parts) == {"type", "template"}
        assert parts["type"].get_payload(decode=True) == b"rate_limit"
        assert parts["template"].get_payload(decode=True) == page
        assert tpl.is_active is False

    @respx.mock
    def test_rejected_page_raises_validation_error(self, client: Ngris) -> None:
        from ngris import ValidationError

        respx.post(f"{BASE}/templates").respond(
            400, json={"error": "Security Check Failed: inline script loads a miner"}
        )
        with pytest.raises(ValidationError, match="Security Check Failed"):
            client.templates.upload("firewall", "<script src=//x></script>")

    @respx.mock
    def test_debug_log_names_the_file_not_its_content(
        self, client: Ngris, caplog: pytest.LogCaptureFixture
    ) -> None:
        respx.post(f"{BASE}/templates").respond(201, json=_stored_template())
        with caplog.at_level("DEBUG", logger="ngris.http"):
            client.templates.upload("not_found", "<h1>secret page body</h1>", active=True)
        sent = [r.getMessage() for r in caplog.records if r.getMessage().startswith("→ POST /templates")]
        assert len(sent) == 1
        assert "<file template.html text/html 25 bytes>" in sent[0]
        assert '"type": "not_found"' in sent[0]
        assert "secret page body" not in sent[0]

    @respx.mock
    async def test_async(self) -> None:
        route = respx.post(f"{BASE}/templates").respond(201, json=_stored_template())
        async with AsyncNgris(api_key="ngris_test", base_url=BASE, max_retries=0, http2=False) as c:
            tpl = await c.templates.upload("not_found", "<h1>Gone</h1>", active=True)
        parts = _multipart(route.calls.last.request)
        assert parts["template"].get_payload(decode=True) == b"<h1>Gone</h1>"
        assert parts["active"].get_payload(decode=True) == b"true"
        assert tpl.uuid == TEMPLATE
