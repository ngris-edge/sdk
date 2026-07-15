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
