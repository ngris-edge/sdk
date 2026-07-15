from __future__ import annotations

from typing import Any

from ngris.services._base import AsyncBaseService, BaseService


class RegionsPlansService(BaseService):
    """Sync regions and plans service."""

    def list_plans(self) -> list[dict[str, Any]]:
        resp = self._client._get("/plans")
        return resp.json()

    def list_regions(self) -> list[dict[str, Any]]:
        resp = self._client._get("/regions")
        return resp.json()

    def list_addons(self) -> list[dict[str, Any]]:
        resp = self._client._get("/addons")
        return resp.json()


class AsyncRegionsPlansService(AsyncBaseService):
    """Async regions and plans service."""

    async def list_plans(self) -> list[dict[str, Any]]:
        resp = await self._client._get("/plans")
        return resp.json()

    async def list_regions(self) -> list[dict[str, Any]]:
        resp = await self._client._get("/regions")
        return resp.json()

    async def list_addons(self) -> list[dict[str, Any]]:
        resp = await self._client._get("/addons")
        return resp.json()
