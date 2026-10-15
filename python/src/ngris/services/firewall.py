from __future__ import annotations

from typing import Any

from ngris.services._base import AsyncBaseService, BaseService, path_id


def _conditions(data: Any) -> list[dict[str, Any]]:
    # GET /firewall/policies/{uuid}/conditions answers {"conditions": [...]}.
    if isinstance(data, dict):
        return list(data.get("conditions") or [])
    return list(data)


class FirewallService(BaseService):
    """Sync firewall service."""

    # --- Policies ---

    def list_policies(self) -> list[dict[str, Any]]:
        resp = self._client._get("/firewall/policies")
        return resp.json()

    def create_policy(self, data: dict[str, Any]) -> dict[str, Any]:
        return self._client._post_raw("/firewall/policies", data)

    def get_policy(self, policy_uuid: str) -> dict[str, Any]:
        return self._client._get_raw(f"/firewall/policies/{policy_uuid}")

    def update_policy(self, policy_uuid: str, data: dict[str, Any]) -> dict[str, Any]:
        return self._client._put_raw(f"/firewall/policies/{policy_uuid}", data)

    def delete_policy(self, policy_uuid: str) -> None:
        self._client._delete_void(f"/firewall/policies/{policy_uuid}")

    # --- Conditions ---

    def list_conditions(self, policy_uuid: str) -> list[dict[str, Any]]:
        resp = self._client._get(f"/firewall/policies/{policy_uuid}/conditions")
        return _conditions(resp.json())

    def create_condition(self, policy_uuid: str, data: dict[str, Any]) -> dict[str, Any]:
        return self._client._post_raw(f"/firewall/policies/{policy_uuid}/conditions", data)

    def update_condition(self, policy_uuid: str, condition_uuid: str, data: dict[str, Any]) -> dict[str, Any]:
        return self._client._put_raw(
            f"/firewall/policies/{policy_uuid}/conditions/{condition_uuid}", data
        )

    def delete_condition(self, policy_uuid: str, condition_uuid: str) -> None:
        self._client._delete_void(f"/firewall/policies/{policy_uuid}/conditions/{condition_uuid}")

    # --- Rate limits ---

    def list_rate_limits(self) -> list[dict[str, Any]]:
        resp = self._client._get("/firewall/rate-limits")
        return resp.json()

    def create_rate_limit(self, data: dict[str, Any]) -> dict[str, Any]:
        return self._client._post_raw("/firewall/rate-limits", data)

    def get_rate_limit(self, rule_uuid: str) -> dict[str, Any]:
        return self._client._get_raw(f"/firewall/rate-limits/{path_id(rule_uuid, 'rule_uuid')}")

    def update_rate_limit(self, rule_uuid: str, data: dict[str, Any]) -> dict[str, Any]:
        return self._client._put_raw(f"/firewall/rate-limits/{path_id(rule_uuid, 'rule_uuid')}", data)

    def delete_rate_limit(self, rule_uuid: str) -> None:
        self._client._delete_void(f"/firewall/rate-limits/{path_id(rule_uuid, 'rule_uuid')}")


class AsyncFirewallService(AsyncBaseService):
    """Async firewall service."""

    # --- Policies ---

    async def list_policies(self) -> list[dict[str, Any]]:
        resp = await self._client._get("/firewall/policies")
        return resp.json()

    async def create_policy(self, data: dict[str, Any]) -> dict[str, Any]:
        return await self._client._post_raw("/firewall/policies", data)

    async def get_policy(self, policy_uuid: str) -> dict[str, Any]:
        return await self._client._get_raw(f"/firewall/policies/{policy_uuid}")

    async def update_policy(self, policy_uuid: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self._client._put_raw(f"/firewall/policies/{policy_uuid}", data)

    async def delete_policy(self, policy_uuid: str) -> None:
        await self._client._delete_void(f"/firewall/policies/{policy_uuid}")

    # --- Conditions ---

    async def list_conditions(self, policy_uuid: str) -> list[dict[str, Any]]:
        resp = await self._client._get(f"/firewall/policies/{policy_uuid}/conditions")
        return _conditions(resp.json())

    async def create_condition(self, policy_uuid: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self._client._post_raw(f"/firewall/policies/{policy_uuid}/conditions", data)

    async def update_condition(self, policy_uuid: str, condition_uuid: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self._client._put_raw(
            f"/firewall/policies/{policy_uuid}/conditions/{condition_uuid}", data
        )

    async def delete_condition(self, policy_uuid: str, condition_uuid: str) -> None:
        await self._client._delete_void(f"/firewall/policies/{policy_uuid}/conditions/{condition_uuid}")

    # --- Rate limits ---

    async def list_rate_limits(self) -> list[dict[str, Any]]:
        resp = await self._client._get("/firewall/rate-limits")
        return resp.json()

    async def create_rate_limit(self, data: dict[str, Any]) -> dict[str, Any]:
        return await self._client._post_raw("/firewall/rate-limits", data)

    async def get_rate_limit(self, rule_uuid: str) -> dict[str, Any]:
        return await self._client._get_raw(f"/firewall/rate-limits/{path_id(rule_uuid, 'rule_uuid')}")

    async def update_rate_limit(self, rule_uuid: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self._client._put_raw(f"/firewall/rate-limits/{path_id(rule_uuid, 'rule_uuid')}", data)

    async def delete_rate_limit(self, rule_uuid: str) -> None:
        await self._client._delete_void(f"/firewall/rate-limits/{path_id(rule_uuid, 'rule_uuid')}")
