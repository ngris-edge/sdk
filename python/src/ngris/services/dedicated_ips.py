from __future__ import annotations

from typing import Any

from ngris.services._base import AsyncBaseService, BaseService


class DedicatedIPsService(BaseService):
    """Sync dedicated IPs service."""

    def list(self) -> list[dict[str, Any]]:
        resp = self._client._get("/dedicated-ips")
        return resp.json()

    def list_requests(self) -> list[dict[str, Any]]:
        resp = self._client._get("/dedicated-ips/requests")
        return resp.json()

    def create_request(self, data: dict[str, Any]) -> dict[str, Any]:
        return self._client._post_raw("/dedicated-ips/requests", data)

    def cancel_request(self, request_id: str) -> None:
        self._client._post_void(f"/dedicated-ips/requests/{request_id}/cancel", {})

    def release(self, ip_id: str) -> None:
        self._client._post_void(f"/dedicated-ips/{ip_id}/release", {})


class AsyncDedicatedIPsService(AsyncBaseService):
    """Async dedicated IPs service."""

    async def list(self) -> list[dict[str, Any]]:
        resp = await self._client._get("/dedicated-ips")
        return resp.json()

    async def list_requests(self) -> list[dict[str, Any]]:
        resp = await self._client._get("/dedicated-ips/requests")
        return resp.json()

    async def create_request(self, data: dict[str, Any]) -> dict[str, Any]:
        return await self._client._post_raw("/dedicated-ips/requests", data)

    async def cancel_request(self, request_id: str) -> None:
        await self._client._post_void(f"/dedicated-ips/requests/{request_id}/cancel", {})

    async def release(self, ip_id: str) -> None:
        await self._client._post_void(f"/dedicated-ips/{ip_id}/release", {})
