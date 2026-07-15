from __future__ import annotations

from typing import Any

from ngris.models.users import UsageTotals, User, UserPlan
from ngris.services._base import AsyncBaseService, BaseService


class UsersService(BaseService):
    """Sync users service."""

    def me(self) -> User:
        """Return the authenticated caller's own profile (GET /user)."""
        return self._client._get_json("/user", User)

    def update(self, user_id: str, data: dict[str, Any]) -> User:
        return self._client._put_json(f"/user/{user_id}", data, User)

    def get_plan(self) -> UserPlan:
        return self._client._get_json("/account/plan", UserPlan)

    def get_entitlements(self) -> dict[str, Any]:
        resp = self._client._get("/account/entitlements")
        return resp.json()

    def get_usage(self) -> UsageTotals:
        return self._client._get_json("/account/usage", UsageTotals)


class AsyncUsersService(AsyncBaseService):
    """Async users service."""

    async def me(self) -> User:
        """Return the authenticated caller's own profile (GET /user)."""
        return await self._client._get_json("/user", User)

    async def update(self, user_id: str, data: dict[str, Any]) -> User:
        return await self._client._put_json(f"/user/{user_id}", data, User)

    async def get_plan(self) -> UserPlan:
        return await self._client._get_json("/account/plan", UserPlan)

    async def get_entitlements(self) -> dict[str, Any]:
        resp = await self._client._get("/account/entitlements")
        return resp.json()

    async def get_usage(self) -> UsageTotals:
        return await self._client._get_json("/account/usage", UsageTotals)
