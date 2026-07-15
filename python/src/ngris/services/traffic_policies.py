from __future__ import annotations

from typing import Any

from ngris.services._base import AsyncBaseService, BaseService


class TrafficPoliciesService(BaseService):
    """Sync traffic policies service."""

    def list(self, endpoint_uuid: str) -> list[dict[str, Any]]:
        resp = self._client._get(f"/endpoints/{endpoint_uuid}/policies")
        return resp.json()

    def create(self, endpoint_uuid: str, data: dict[str, Any]) -> dict[str, Any]:
        return self._client._post_raw(f"/endpoints/{endpoint_uuid}/policies", data)

    def get(self, endpoint_uuid: str, policy_id: str) -> dict[str, Any]:
        return self._client._get_raw(f"/endpoints/{endpoint_uuid}/policies/{policy_id}")

    def update(self, endpoint_uuid: str, policy_id: str, data: dict[str, Any]) -> dict[str, Any]:
        return self._client._put_raw(f"/endpoints/{endpoint_uuid}/policies/{policy_id}", data)

    def delete(self, endpoint_uuid: str, policy_id: str) -> None:
        self._client._delete_void(f"/endpoints/{endpoint_uuid}/policies/{policy_id}")

    def create_rule(self, endpoint_uuid: str, policy_id: str, data: dict[str, Any]) -> dict[str, Any]:
        return self._client._post_raw(
            f"/endpoints/{endpoint_uuid}/policies/{policy_id}/rules", data
        )

    def update_rule(self, endpoint_uuid: str, policy_id: str, rule_id: str, data: dict[str, Any]) -> dict[str, Any]:
        return self._client._put_raw(
            f"/endpoints/{endpoint_uuid}/policies/{policy_id}/rules/{rule_id}", data
        )

    def delete_rule(self, endpoint_uuid: str, policy_id: str, rule_id: str) -> None:
        self._client._delete_void(
            f"/endpoints/{endpoint_uuid}/policies/{policy_id}/rules/{rule_id}"
        )


class AsyncTrafficPoliciesService(AsyncBaseService):
    """Async traffic policies service."""

    async def list(self, endpoint_uuid: str) -> list[dict[str, Any]]:
        resp = await self._client._get(f"/endpoints/{endpoint_uuid}/policies")
        return resp.json()

    async def create(self, endpoint_uuid: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self._client._post_raw(f"/endpoints/{endpoint_uuid}/policies", data)

    async def get(self, endpoint_uuid: str, policy_id: str) -> dict[str, Any]:
        return await self._client._get_raw(f"/endpoints/{endpoint_uuid}/policies/{policy_id}")

    async def update(self, endpoint_uuid: str, policy_id: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self._client._put_raw(f"/endpoints/{endpoint_uuid}/policies/{policy_id}", data)

    async def delete(self, endpoint_uuid: str, policy_id: str) -> None:
        await self._client._delete_void(f"/endpoints/{endpoint_uuid}/policies/{policy_id}")

    async def create_rule(self, endpoint_uuid: str, policy_id: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self._client._post_raw(
            f"/endpoints/{endpoint_uuid}/policies/{policy_id}/rules", data
        )

    async def update_rule(self, endpoint_uuid: str, policy_id: str, rule_id: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self._client._put_raw(
            f"/endpoints/{endpoint_uuid}/policies/{policy_id}/rules/{rule_id}", data
        )

    async def delete_rule(self, endpoint_uuid: str, policy_id: str, rule_id: str) -> None:
        await self._client._delete_void(
            f"/endpoints/{endpoint_uuid}/policies/{policy_id}/rules/{rule_id}"
        )
