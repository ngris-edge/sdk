from __future__ import annotations

from typing import Any

from ngris._pagination import PaginatedResponse
from ngris.models.traffic import TrafficLog
from ngris.services._base import AsyncBaseService, BaseService


class TrafficService(BaseService):
    """Sync traffic service."""

    def list_logs(self, page: int = 1, page_size: int = 50) -> PaginatedResponse[TrafficLog]:
        return self._client._get_page("/traffic/logs", TrafficLog, page=page, page_size=page_size)

    def get_log(self, log_id: str) -> dict[str, Any]:
        return self._client._get_raw(f"/traffic/logs/{log_id}")

    def replay_log(self, log_id: str) -> dict[str, Any]:
        return self._client._post_raw(f"/traffic/logs/{log_id}/replay", {})

    def analyze_log(self, log_id: str) -> dict[str, Any]:
        return self._client._post_raw(f"/traffic/logs/{log_id}/analyze", {})

    def get_metrics(self) -> dict[str, Any]:
        return self._client._get_raw("/traffic/metrics")

    def smart_search(self, query: str) -> dict[str, Any]:
        return self._client._post_raw("/traffic/smart-search", {"query": query})


class AsyncTrafficService(AsyncBaseService):
    """Async traffic service."""

    async def list_logs(self, page: int = 1, page_size: int = 50) -> PaginatedResponse[TrafficLog]:
        return await self._client._get_page("/traffic/logs", TrafficLog, page=page, page_size=page_size)

    async def get_log(self, log_id: str) -> dict[str, Any]:
        return await self._client._get_raw(f"/traffic/logs/{log_id}")

    async def replay_log(self, log_id: str) -> dict[str, Any]:
        return await self._client._post_raw(f"/traffic/logs/{log_id}/replay", {})

    async def analyze_log(self, log_id: str) -> dict[str, Any]:
        return await self._client._post_raw(f"/traffic/logs/{log_id}/analyze", {})

    async def get_metrics(self) -> dict[str, Any]:
        return await self._client._get_raw("/traffic/metrics")

    async def smart_search(self, query: str) -> dict[str, Any]:
        return await self._client._post_raw("/traffic/smart-search", {"query": query})
