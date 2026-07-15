from __future__ import annotations

import pytest
import respx

from ngris import Ngris
from ngris.models.endpoints import Endpoint

_ENDPOINT = {
    "id": 1,
    "uuid": "a",
    "user_id": 1,
    "subdomain": "app",
    "protocol": "http",
    "region": "eu-north-1",
    "is_custom": False,
    "status": "active",
    "mtls_mode": "disabled",
    "ephemeral": False,
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": "2026-01-01T00:00:00Z",
}


class TestPagination:
    def test_get_page(self, client, mock_api):
        ep1 = {**_ENDPOINT, "id": 1, "uuid": "a"}
        ep2 = {**_ENDPOINT, "id": 2, "uuid": "b"}
        mock_api.get("/endpoints").respond(
            200, json={"items": [ep1, ep2], "total": 5, "page": 1}
        )
        page = client._get_page("/endpoints", Endpoint, page=1, page_size=2)
        assert len(page.items) == 2
        assert page.total == 5
        assert page.page == 1
        assert page.has_more

    def test_autopage(self, client, mock_api):
        ep1 = {**_ENDPOINT, "id": 1, "uuid": "a"}
        ep2 = {**_ENDPOINT, "id": 2, "uuid": "b", "subdomain": "api"}

        route = mock_api.get("/endpoints")
        route.side_effect = [
            respx.MockResponse(200, json={"items": [ep1], "total": 2, "page": 1}),
            respx.MockResponse(200, json={"items": [ep2], "total": 2, "page": 2}),
        ]

        all_items = list(client._autopage("/endpoints", Endpoint, page_size=1))
        assert len(all_items) == 2
        assert all_items[0].uuid == "a"
        assert all_items[1].uuid == "b"
