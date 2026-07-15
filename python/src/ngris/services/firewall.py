from __future__ import annotations

from typing import Any

from ngris.services._base import AsyncBaseService, BaseService


class FirewallService(BaseService):
    """Sync firewall service."""

    # --- Policies ---

    def list_policies(self) -> list[dict[str, Any]]:
        resp = self._client._get("/firewall/policies")
        return resp.json()

    def create_policy(self, data: dict[str, Any]) -> dict[str, Any]:
        return self._client._post_raw("/firewall/policies", data)

    def get_policy(self, policy_id: str) -> dict[str, Any]:
        return self._client._get_raw(f"/firewall/policies/{policy_id}")

    def update_policy(self, policy_id: str, data: dict[str, Any]) -> dict[str, Any]:
        return self._client._put_raw(f"/firewall/policies/{policy_id}", data)

    def delete_policy(self, policy_id: str) -> None:
        self._client._delete_void(f"/firewall/policies/{policy_id}")

    # --- Conditions ---

    def list_conditions(self, policy_id: str) -> list[dict[str, Any]]:
        resp = self._client._get(f"/firewall/policies/{policy_id}/conditions")
        return resp.json()

    def create_condition(self, policy_id: str, data: dict[str, Any]) -> dict[str, Any]:
        return self._client._post_raw(f"/firewall/policies/{policy_id}/conditions", data)

    def update_condition(self, policy_id: str, condition_id: str, data: dict[str, Any]) -> dict[str, Any]:
        return self._client._put_raw(
            f"/firewall/policies/{policy_id}/conditions/{condition_id}", data
        )

    def delete_condition(self, policy_id: str, condition_id: str) -> None:
        self._client._delete_void(f"/firewall/policies/{policy_id}/conditions/{condition_id}")

    # --- Rate limits ---

    def list_rate_limits(self) -> list[dict[str, Any]]:
        resp = self._client._get("/firewall/rate-limits")
        return resp.json()

    def create_rate_limit(self, data: dict[str, Any]) -> dict[str, Any]:
        return self._client._post_raw("/firewall/rate-limits", data)

    def get_rate_limit(self, rule_id: str) -> dict[str, Any]:
        return self._client._get_raw(f"/firewall/rate-limits/{rule_id}")

    def update_rate_limit(self, rule_id: str, data: dict[str, Any]) -> dict[str, Any]:
        return self._client._put_raw(f"/firewall/rate-limits/{rule_id}", data)

    def delete_rate_limit(self, rule_id: str) -> None:
        self._client._delete_void(f"/firewall/rate-limits/{rule_id}")


class AsyncFirewallService(AsyncBaseService):
    """Async firewall service."""

    # --- Policies ---

    async def list_policies(self) -> list[dict[str, Any]]:
        resp = await self._client._get("/firewall/policies")
        return resp.json()

    async def create_policy(self, data: dict[str, Any]) -> dict[str, Any]:
        return await self._client._post_raw("/firewall/policies", data)

    async def get_policy(self, policy_id: str) -> dict[str, Any]:
        return await self._client._get_raw(f"/firewall/policies/{policy_id}")

    async def update_policy(self, policy_id: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self._client._put_raw(f"/firewall/policies/{policy_id}", data)

    async def delete_policy(self, policy_id: str) -> None:
        await self._client._delete_void(f"/firewall/policies/{policy_id}")

    # --- Conditions ---

    async def list_conditions(self, policy_id: str) -> list[dict[str, Any]]:
        resp = await self._client._get(f"/firewall/policies/{policy_id}/conditions")
        return resp.json()

    async def create_condition(self, policy_id: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self._client._post_raw(f"/firewall/policies/{policy_id}/conditions", data)

    async def update_condition(self, policy_id: str, condition_id: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self._client._put_raw(
            f"/firewall/policies/{policy_id}/conditions/{condition_id}", data
        )

    async def delete_condition(self, policy_id: str, condition_id: str) -> None:
        await self._client._delete_void(f"/firewall/policies/{policy_id}/conditions/{condition_id}")

    # --- Rate limits ---

    async def list_rate_limits(self) -> list[dict[str, Any]]:
        resp = await self._client._get("/firewall/rate-limits")
        return resp.json()

    async def create_rate_limit(self, data: dict[str, Any]) -> dict[str, Any]:
        return await self._client._post_raw("/firewall/rate-limits", data)

    async def get_rate_limit(self, rule_id: str) -> dict[str, Any]:
        return await self._client._get_raw(f"/firewall/rate-limits/{rule_id}")

    async def update_rate_limit(self, rule_id: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self._client._put_raw(f"/firewall/rate-limits/{rule_id}", data)

    async def delete_rate_limit(self, rule_id: str) -> None:
        await self._client._delete_void(f"/firewall/rate-limits/{rule_id}")
