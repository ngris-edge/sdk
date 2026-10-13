from __future__ import annotations

from typing import Any

from ngris.services._base import AsyncBaseService, BaseService, path_id


def _policies(data: Any) -> list[dict[str, Any]]:
    # GET /endpoints/{uuid}/policies answers {"policies": [...]}.
    if isinstance(data, dict):
        return list(data.get("policies") or [])
    return list(data)


def _policy_path(endpoint_uuid: str, policy_uuid: str) -> str:
    return f"/endpoints/{endpoint_uuid}/policies/{path_id(policy_uuid, 'policy_uuid')}"


def _rule_path(endpoint_uuid: str, policy_uuid: str, rule_uuid: str) -> str:
    return f"{_policy_path(endpoint_uuid, policy_uuid)}/rules/{path_id(rule_uuid, 'rule_uuid')}"


class TrafficPoliciesService(BaseService):
    """Sync traffic policies service.

    Policies and rules are addressed by their ``uuid``; a policy rule resolves
    only under its policy, a policy only under its endpoint.
    """

    def list(self, endpoint_uuid: str) -> list[dict[str, Any]]:
        resp = self._client._get(f"/endpoints/{endpoint_uuid}/policies")
        return _policies(resp.json())

    def create(self, endpoint_uuid: str, data: dict[str, Any]) -> dict[str, Any]:
        return self._client._post_raw(f"/endpoints/{endpoint_uuid}/policies", data)

    def get(self, endpoint_uuid: str, policy_uuid: str) -> dict[str, Any]:
        return self._client._get_raw(_policy_path(endpoint_uuid, policy_uuid))

    def update(self, endpoint_uuid: str, policy_uuid: str, data: dict[str, Any]) -> dict[str, Any]:
        return self._client._put_raw(_policy_path(endpoint_uuid, policy_uuid), data)

    def delete(self, endpoint_uuid: str, policy_uuid: str) -> None:
        self._client._delete_void(_policy_path(endpoint_uuid, policy_uuid))

    def create_rule(self, endpoint_uuid: str, policy_uuid: str, data: dict[str, Any]) -> dict[str, Any]:
        return self._client._post_raw(f"{_policy_path(endpoint_uuid, policy_uuid)}/rules", data)

    def update_rule(
        self, endpoint_uuid: str, policy_uuid: str, rule_uuid: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        return self._client._put_raw(_rule_path(endpoint_uuid, policy_uuid, rule_uuid), data)

    def delete_rule(self, endpoint_uuid: str, policy_uuid: str, rule_uuid: str) -> None:
        self._client._delete_void(_rule_path(endpoint_uuid, policy_uuid, rule_uuid))


class AsyncTrafficPoliciesService(AsyncBaseService):
    """Async traffic policies service."""

    async def list(self, endpoint_uuid: str) -> list[dict[str, Any]]:
        resp = await self._client._get(f"/endpoints/{endpoint_uuid}/policies")
        return _policies(resp.json())

    async def create(self, endpoint_uuid: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self._client._post_raw(f"/endpoints/{endpoint_uuid}/policies", data)

    async def get(self, endpoint_uuid: str, policy_uuid: str) -> dict[str, Any]:
        return await self._client._get_raw(_policy_path(endpoint_uuid, policy_uuid))

    async def update(self, endpoint_uuid: str, policy_uuid: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self._client._put_raw(_policy_path(endpoint_uuid, policy_uuid), data)

    async def delete(self, endpoint_uuid: str, policy_uuid: str) -> None:
        await self._client._delete_void(_policy_path(endpoint_uuid, policy_uuid))

    async def create_rule(self, endpoint_uuid: str, policy_uuid: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self._client._post_raw(f"{_policy_path(endpoint_uuid, policy_uuid)}/rules", data)

    async def update_rule(
        self, endpoint_uuid: str, policy_uuid: str, rule_uuid: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        return await self._client._put_raw(_rule_path(endpoint_uuid, policy_uuid, rule_uuid), data)

    async def delete_rule(self, endpoint_uuid: str, policy_uuid: str, rule_uuid: str) -> None:
        await self._client._delete_void(_rule_path(endpoint_uuid, policy_uuid, rule_uuid))
