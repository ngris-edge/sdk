"""Async client tests.

Two layers:

1. *Parity* — mirror the sync tests (auth header, error mapping, retry,
   pagination). Without this, an async-only regression in
   :class:`AsyncBaseClient` slips through, since the sync tests exercise
   only :class:`SyncBaseClient`.

2. *Async-only* — three scenarios that don't exist on the sync side and
   would be silent footguns if untested:

   - ``asyncio.gather`` of many concurrent requests on a single client
   - task cancellation mid-request leaving the client usable afterwards
   - ``async for`` over the auto-pager

The pyproject is configured with ``asyncio_mode = auto``, so plain
``async def`` test functions just work — no ``@pytest.mark.asyncio``
decorator needed.
"""

from __future__ import annotations

import asyncio

import httpx
import pytest
import respx

from ngris import (
    AsyncNgris,
    AuthenticationError,
    NgrisConnectionError,
    NotFoundError,
    ServerError,
)
from ngris.models.endpoints import Endpoint

# Reused fixture — keeps every test row identical to the sync pagination
# fixture so any drift in Endpoint shape is caught here too.
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


class TestAsyncAuth:
    @respx.mock
    async def test_sends_api_key_header(self, async_client: AsyncNgris) -> None:
        route = respx.get("https://api.ngris.io/test").respond(200, json={"ok": True})
        await async_client._get("/test")
        sent = route.calls.last.request
        assert sent.headers["X-API-Key"] == "ngris_test_abcdef123456"
        assert sent.headers["Accept"] == "application/json"

    @respx.mock
    async def test_sends_content_type_with_body(self, async_client: AsyncNgris) -> None:
        route = respx.post("https://api.ngris.io/test").respond(200, json={"ok": True})
        await async_client._post("/test", body={"k": "v"})
        assert route.calls.last.request.headers["Content-Type"] == "application/json"


class TestAsyncErrors:
    @respx.mock
    async def test_401_raises_auth_error(self, async_client: AsyncNgris) -> None:
        respx.get("https://api.ngris.io/test").respond(
            401, json={"error": "Unauthorized"}
        )
        with pytest.raises(AuthenticationError):
            await async_client._get("/test")

    @respx.mock
    async def test_404_raises_not_found(self, async_client: AsyncNgris) -> None:
        respx.get("https://api.ngris.io/test/missing").respond(
            404, json={"error": "Not found"}
        )
        with pytest.raises(NotFoundError):
            await async_client._get("/test/missing")

    @respx.mock
    async def test_delete_void_swallows_404(self, async_client: AsyncNgris) -> None:
        respx.delete("https://api.ngris.io/test/gone").respond(404, json={"error": "x"})
        # Must not raise — delete-then-not-found is treated as success
        # so callers can re-issue idempotently.
        await async_client._delete_void("/test/gone")

    @respx.mock
    async def test_request_id_attached_to_async_error(
        self, async_client: AsyncNgris
    ) -> None:
        respx.get("https://api.ngris.io/test").respond(
            401,
            json={"error": "bad key"},
            headers={"X-Request-ID": "req-async-1"},
        )
        with pytest.raises(AuthenticationError) as ei:
            await async_client._get("/test")
        assert ei.value.request_id == "req-async-1"


class TestAsyncRetry:
    @respx.mock
    async def test_retries_on_500(self, api_key, base_url) -> None:
        respx.get(f"{base_url}/test").mock(
            side_effect=[
                httpx.Response(500, json={"error": "down"}),
                httpx.Response(200, json={"ok": True}),
            ]
        )
        async with AsyncNgris(
            api_key=api_key, base_url=base_url, max_retries=1, backoff_factor=0
        ) as c:
            resp = await c._get("/test")
            assert resp.status_code == 200

    @respx.mock
    async def test_raises_after_max_retries(self, api_key, base_url) -> None:
        respx.get(f"{base_url}/test").respond(500, json={"error": "still down"})
        async with AsyncNgris(
            api_key=api_key, base_url=base_url, max_retries=1, backoff_factor=0
        ) as c:
            with pytest.raises(ServerError):
                await c._get("/test")


class TestAsyncPagination:
    @respx.mock
    async def test_get_page(self, async_client: AsyncNgris) -> None:
        ep1 = {**_ENDPOINT, "id": 1, "uuid": "a"}
        ep2 = {**_ENDPOINT, "id": 2, "uuid": "b"}
        respx.get("https://api.ngris.io/endpoints").respond(
            200, json={"items": [ep1, ep2], "total": 5, "page": 1}
        )
        page = await async_client._get_page("/endpoints", Endpoint, page=1, page_size=2)
        assert len(page.items) == 2
        assert page.total == 5
        assert page.has_more

    @respx.mock
    async def test_async_for_autopage(self, async_client: AsyncNgris) -> None:
        """Iterate the pager with ``async for`` — the canonical async usage.

        Using ``async for`` (not manual ``__anext__`` calls) ensures the
        iterator integrates with normal async control flow and that
        StopAsyncIteration is raised at the right moment.
        """
        ep1 = {**_ENDPOINT, "id": 1, "uuid": "a"}
        ep2 = {**_ENDPOINT, "id": 2, "uuid": "b", "subdomain": "api"}

        route = respx.get("https://api.ngris.io/endpoints")
        route.side_effect = [
            httpx.Response(200, json={"items": [ep1], "total": 2, "page": 1}),
            httpx.Response(200, json={"items": [ep2], "total": 2, "page": 2}),
        ]

        collected: list[Endpoint] = []
        async for item in async_client._autopage("/endpoints", Endpoint, page_size=1):
            collected.append(item)

        assert [e.uuid for e in collected] == ["a", "b"]


# ──────────────────────────────────────────────────────────────────────
# Async-only behaviours — these can't exist on the sync client.
# ──────────────────────────────────────────────────────────────────────


class TestAsyncConcurrency:
    """Properties that only an async client has to get right: shared
    connection pool under concurrent load, and graceful cancellation."""

    @respx.mock
    async def test_gather_many_requests_share_one_client(
        self, async_client: AsyncNgris
    ) -> None:
        """Fire 20 concurrent GETs through one client. They must all
        succeed and the underlying httpx.AsyncClient must serve every
        one — a regression where the SDK accidentally creates a fresh
        client per request would still pass this test functionally, but
        a regression that mishandles the pool (e.g., closes after first
        request) would surface here as a cascade of failures.
        """
        respx.get("https://api.ngris.io/ping").respond(200, json={"ok": True})
        results = await asyncio.gather(
            *(async_client._get("/ping") for _ in range(20))
        )
        assert len(results) == 20
        assert all(r.status_code == 200 for r in results)

    @respx.mock
    async def test_cancel_does_not_poison_client(
        self, async_client: AsyncNgris
    ) -> None:
        """Cancel a request mid-flight, then issue a fresh one on the
        same client. The second request must succeed — i.e., the client
        is still usable after a CancelledError tears down a task.

        The first response is wired to a slow handler. We start it,
        cancel after a tick, then issue a clean GET against a different
        path with a fast handler.
        """

        async def slow_handler(request: httpx.Request) -> httpx.Response:
            # Long enough that the cancel always wins the race.
            await asyncio.sleep(5.0)
            return httpx.Response(200, json={"never": "reached"})

        respx.get("https://api.ngris.io/slow").mock(side_effect=slow_handler)
        respx.get("https://api.ngris.io/fast").respond(200, json={"ok": True})

        task = asyncio.create_task(async_client._get("/slow"))
        # Give the request a chance to start before we cancel it.
        await asyncio.sleep(0.05)
        task.cancel()
        with pytest.raises((asyncio.CancelledError, Exception)):
            await task

        # Same client, brand new request — must work.
        resp = await async_client._get("/fast")
        assert resp.status_code == 200

    @respx.mock
    async def test_connect_error_in_one_task_does_not_break_others(
        self, async_client: AsyncNgris
    ) -> None:
        """Failure isolation under gather(): one task hitting a connect
        error must not cause sibling tasks to fail."""
        respx.get("https://api.ngris.io/good").respond(200, json={"ok": True})
        respx.get("https://api.ngris.io/bad").mock(
            side_effect=httpx.ConnectError("nope")
        )

        good_task = async_client._get("/good")
        bad_task = async_client._get("/bad")

        results = await asyncio.gather(good_task, bad_task, return_exceptions=True)
        good, bad = results
        assert isinstance(good, httpx.Response) and good.status_code == 200
        assert isinstance(bad, NgrisConnectionError)
