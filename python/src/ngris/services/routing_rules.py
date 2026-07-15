from __future__ import annotations

from typing import Any

from ngris.models.routing_rules import RoutingRule
from ngris.services._base import AsyncBaseService, BaseService


class RoutingRulesService(BaseService):
    """Sync routing rules service."""

    def list(self, endpoint_uuid: str) -> list[RoutingRule]:
        resp = self._client._get(f"/endpoints/{endpoint_uuid}/routing-rules")
        data = resp.json()
        return [RoutingRule.model_validate(item) for item in data]

    def create(self, endpoint_uuid: str, data: dict[str, Any]) -> RoutingRule:
        return self._client._post_json(f"/endpoints/{endpoint_uuid}/routing-rules", data, RoutingRule)

    def get(self, endpoint_uuid: str, rule_id: str) -> RoutingRule:
        return self._client._get_json(f"/endpoints/{endpoint_uuid}/routing-rules/{rule_id}", RoutingRule)

    def update(self, endpoint_uuid: str, rule_id: str, data: dict[str, Any]) -> RoutingRule:
        return self._client._put_json(f"/endpoints/{endpoint_uuid}/routing-rules/{rule_id}", data, RoutingRule)

    def delete(self, endpoint_uuid: str, rule_id: str) -> None:
        self._client._delete_void(f"/endpoints/{endpoint_uuid}/routing-rules/{rule_id}")


class AsyncRoutingRulesService(AsyncBaseService):
    """Async routing rules service."""

    async def list(self, endpoint_uuid: str) -> list[RoutingRule]:
        resp = await self._client._get(f"/endpoints/{endpoint_uuid}/routing-rules")
        data = resp.json()
        return [RoutingRule.model_validate(item) for item in data]

    async def create(self, endpoint_uuid: str, data: dict[str, Any]) -> RoutingRule:
        return await self._client._post_json(f"/endpoints/{endpoint_uuid}/routing-rules", data, RoutingRule)

    async def get(self, endpoint_uuid: str, rule_id: str) -> RoutingRule:
        return await self._client._get_json(f"/endpoints/{endpoint_uuid}/routing-rules/{rule_id}", RoutingRule)

    async def update(self, endpoint_uuid: str, rule_id: str, data: dict[str, Any]) -> RoutingRule:
        return await self._client._put_json(f"/endpoints/{endpoint_uuid}/routing-rules/{rule_id}", data, RoutingRule)

    async def delete(self, endpoint_uuid: str, rule_id: str) -> None:
        await self._client._delete_void(f"/endpoints/{endpoint_uuid}/routing-rules/{rule_id}")
