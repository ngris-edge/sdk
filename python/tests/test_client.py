from __future__ import annotations

import pytest
import respx

from ngris import Ngris, AuthenticationError, NotFoundError


class TestClientAuth:
    def test_sends_api_key_header(self, client, mock_api):
        mock_api.get("/test").respond(200, json={"ok": True})
        resp = client._get("/test")
        assert resp.status_code == 200
        sent_req = mock_api.calls.last.request
        assert sent_req.headers["X-API-Key"] == "ngris_test_abcdef123456"
        assert sent_req.headers["Accept"] == "application/json"

    def test_sends_content_type_with_body(self, client, mock_api):
        mock_api.post("/test").respond(200, json={"ok": True})
        client._post("/test", body={"key": "value"})
        sent_req = mock_api.calls.last.request
        assert sent_req.headers["Content-Type"] == "application/json"


class TestClientErrors:
    def test_401_raises_auth_error(self, client, mock_api):
        mock_api.get("/test").respond(401, json={"error": "Unauthorized"})
        with pytest.raises(AuthenticationError):
            client._get("/test")

    def test_404_raises_not_found(self, client, mock_api):
        mock_api.get("/test/missing").respond(404, json={"error": "Not found"})
        with pytest.raises(NotFoundError):
            client._get("/test/missing")

    def test_delete_void_treats_404_as_success(self, client, mock_api):
        mock_api.delete("/test/gone").respond(404, json={"error": "Not found"})
        # Should NOT raise
        client._delete_void("/test/gone")

    def test_delete_void_succeeds_on_204(self, client, mock_api):
        mock_api.delete("/test/ok").respond(204)
        client._delete_void("/test/ok")


class TestClientContextManager:
    def test_context_manager(self, api_key, base_url):
        with Ngris(api_key=api_key, base_url=base_url) as client:
            assert client._config.api_key == api_key


class TestDefaultBaseURL:
    """With no base_url and no NGRIS_BASE_URL the client calls the management
    API at https://api.ngris.com/v1 (api-server serves /v1/... as /api/v1/...),
    each service path appended as-is."""

    def test_default_is_the_v1_api(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("NGRIS_BASE_URL", raising=False)
        with Ngris(api_key="ngris_test", http2=False) as client:
            assert client._config.base_url == "https://api.ngris.com/v1"

    @respx.mock
    def test_default_request_url(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("NGRIS_BASE_URL", raising=False)
        route = respx.get("https://api.ngris.com/v1/endpoints/019bb1e4-e785-77d2-9966-c3cff31d0a0e/settings").respond(
            200, json={"mode": "none"}
        )
        with Ngris(api_key="ngris_test", http2=False, max_retries=0) as client:
            client.endpoints.get_settings("019bb1e4-e785-77d2-9966-c3cff31d0a0e")
        assert str(route.calls.last.request.url) == (
            "https://api.ngris.com/v1/endpoints/019bb1e4-e785-77d2-9966-c3cff31d0a0e/settings"
        )

    @respx.mock
    def test_trailing_slash_and_env_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("NGRIS_BASE_URL", "https://api.staging.example/v1/")
        route = respx.get("https://api.staging.example/v1/plans").respond(200, json=[])
        with Ngris(api_key="ngris_test", http2=False, max_retries=0) as client:
            client._get("/plans")
        assert str(route.calls.last.request.url) == "https://api.staging.example/v1/plans"
