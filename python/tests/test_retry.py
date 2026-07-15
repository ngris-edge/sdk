from __future__ import annotations

import pytest
import respx

from ngris import Ngris, ServerError


class TestRetry:
    def test_retries_on_500(self, api_key, base_url, mock_api):
        route = mock_api.get("/test")
        route.side_effect = [
            respx.MockResponse(500, json={"error": "Internal"}),
            respx.MockResponse(200, json={"ok": True}),
        ]
        client = Ngris(api_key=api_key, base_url=base_url, max_retries=1, backoff_factor=0)
        try:
            resp = client._get("/test")
            assert resp.status_code == 200
        finally:
            client.close()

    def test_raises_after_max_retries(self, api_key, base_url, mock_api):
        mock_api.get("/test").respond(500, json={"error": "Down"})
        client = Ngris(api_key=api_key, base_url=base_url, max_retries=1, backoff_factor=0)
        try:
            with pytest.raises(ServerError):
                client._get("/test")
        finally:
            client.close()
