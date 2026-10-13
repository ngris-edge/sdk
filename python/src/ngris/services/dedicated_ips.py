from __future__ import annotations

from typing import Any

from ngris.services._base import AsyncBaseService, BaseService, path_id


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

    def cancel_request(self, request_uuid: str) -> None:
        self._client._post_void(f"/dedicated-ips/requests/{path_id(request_uuid, 'request_uuid')}/cancel", {})

    def release(self, assignment_uuid: str) -> None:
        """Release a dedicated IP: pass the assignment's ``uuid`` (an item of :meth:`list`)."""
        self._client._post_void(f"/dedicated-ips/{path_id(assignment_uuid, 'assignment_uuid')}/release", {})


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

    async def cancel_request(self, request_uuid: str) -> None:
        await self._client._post_void(f"/dedicated-ips/requests/{path_id(request_uuid, 'request_uuid')}/cancel", {})

    async def release(self, assignment_uuid: str) -> None:
        await self._client._post_void(f"/dedicated-ips/{path_id(assignment_uuid, 'assignment_uuid')}/release", {})
