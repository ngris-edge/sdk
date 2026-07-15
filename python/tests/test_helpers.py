"""Tests for the ``_*_raw`` and ``_*_void`` client helpers.

These helpers replaced ~67 ``# type: ignore[type-abstract]`` comments
across the services. The contract worth pinning:

  * ``_*_raw`` returns a plain ``dict[str, Any]`` (not a Pydantic model)
    and normalises non-dict JSON into a dict shape.
  * ``_*_void`` discards the response body — no parse, no return value.
  * 204 / empty responses return ``{}`` from ``_*_raw`` rather than
    blowing up on the JSON decoder.
"""

from __future__ import annotations

import pytest
import respx

from ngris import AsyncNgris, MalformedResponseError, Ngris


class TestRawHelpersSync:
    def test_get_raw_returns_dict(self, client: Ngris, mock_api) -> None:
        mock_api.get("/x").respond(200, json={"a": 1, "b": "ok"})
        out = client._get_raw("/x")
        assert out == {"a": 1, "b": "ok"}
        assert isinstance(out, dict)

    def test_post_raw_returns_dict(self, client: Ngris, mock_api) -> None:
        mock_api.post("/x").respond(200, json={"id": 42})
        assert client._post_raw("/x", {"q": 1}) == {"id": 42}

    def test_put_raw_returns_dict(self, client: Ngris, mock_api) -> None:
        mock_api.put("/x").respond(200, json={"updated": True})
        assert client._put_raw("/x", {"q": 1}) == {"updated": True}

    def test_raw_normalises_list_response(self, client: Ngris, mock_api) -> None:
        # Some endpoints return a bare JSON array. The raw helper wraps
        # to {"items": [...]} so callers always get a dict shape.
        mock_api.get("/list").respond(200, json=[{"id": 1}, {"id": 2}])
        out = client._get_raw("/list")
        assert out == {"items": [{"id": 1}, {"id": 2}]}

    def test_raw_normalises_scalar_response(self, client: Ngris, mock_api) -> None:
        mock_api.get("/n").respond(200, json=42)
        assert client._get_raw("/n") == {"value": 42}

    def test_raw_empty_204_returns_empty_dict(self, client: Ngris, mock_api) -> None:
        mock_api.get("/x").respond(204)
        assert client._get_raw("/x") == {}

    def test_raw_non_json_raises_malformed(self, client: Ngris, mock_api) -> None:
        mock_api.get("/bad").respond(
            200, content=b"<html>oh no</html>", headers={"content-type": "text/html"}
        )
        with pytest.raises(MalformedResponseError):
            client._get_raw("/bad")


class TestVoidHelpersSync:
    def test_post_void_returns_none(self, client: Ngris, mock_api) -> None:
        mock_api.post("/x").respond(204)
        # Even when the server *does* send a body, _post_void must
        # discard it and return None — proves the helper isn't silently
        # falling back to JSON parsing.
        assert client._post_void("/x", {"k": "v"}) is None

    def test_post_void_ignores_response_body(self, client: Ngris, mock_api) -> None:
        mock_api.post("/x").respond(200, json={"unused": True})
        assert client._post_void("/x", {}) is None

    def test_put_void_returns_none(self, client: Ngris, mock_api) -> None:
        mock_api.put("/x").respond(204)
        assert client._put_void("/x", {"k": "v"}) is None

    def test_get_void_returns_none(self, client: Ngris, mock_api) -> None:
        mock_api.get("/verify").respond(200, json={"message": "ok"})
        assert client._get_void("/verify", params={"token": "t"}) is None


class TestRawHelpersAsync:
    @respx.mock
    async def test_async_get_raw(self, async_client: AsyncNgris) -> None:
        respx.get("https://api.ngris.io/x").respond(200, json={"a": 1})
        assert await async_client._get_raw("/x") == {"a": 1}

    @respx.mock
    async def test_async_post_raw(self, async_client: AsyncNgris) -> None:
        respx.post("https://api.ngris.io/x").respond(200, json={"id": 1})
        assert await async_client._post_raw("/x", {"q": 1}) == {"id": 1}

    @respx.mock
    async def test_async_put_raw(self, async_client: AsyncNgris) -> None:
        respx.put("https://api.ngris.io/x").respond(200, json={"updated": True})
        assert await async_client._put_raw("/x", {"q": 1}) == {"updated": True}


class TestVoidHelpersAsync:
    @respx.mock
    async def test_async_post_void(self, async_client: AsyncNgris) -> None:
        respx.post("https://api.ngris.io/x").respond(204)
        assert await async_client._post_void("/x", {}) is None

    @respx.mock
    async def test_async_put_void(self, async_client: AsyncNgris) -> None:
        respx.put("https://api.ngris.io/x").respond(204)
        assert await async_client._put_void("/x", {}) is None

    @respx.mock
    async def test_async_get_void(self, async_client: AsyncNgris) -> None:
        respx.get("https://api.ngris.io/verify").respond(200, json={"x": 1})
        assert await async_client._get_void("/verify") is None
