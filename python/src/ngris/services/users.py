from __future__ import annotations

import warnings
from typing import Any

from ngris.models.users import UsageTotals, UserPlan, UserProfile
from ngris.services._base import PUBLIC_IDS_DOCS, AsyncBaseService, BaseService


def _profile_body(
    data: dict[str, Any] | str | int, legacy_data: dict[str, Any] | None
) -> dict[str, Any]:
    # update(user_id, data) is the deprecated 0.1 form: the profile route is
    # PUT /user (the caller's own profile), so the user id is ignored.
    if legacy_data is not None:
        warnings.warn(
            f"update(user_id, data) is deprecated; call update(data) (see {PUBLIC_IDS_DOCS})",
            DeprecationWarning,
            stacklevel=3,
        )
        return legacy_data
    if not isinstance(data, dict):
        raise TypeError("update() takes the profile fields as a dict")
    return data


class UsersService(BaseService):
    """Sync users service."""

    def me(self) -> UserProfile:
        """Return the authenticated caller's own profile (GET /user)."""
        return self._client._get_json("/user", UserProfile)

    def update(self, data: dict[str, Any] | str | int, legacy_data: dict[str, Any] | None = None) -> UserProfile:
        """Update the caller's own profile (PUT /user); returns the updated profile."""
        return self._client._put_json("/user", _profile_body(data, legacy_data), UserProfile)

    def get_plan(self) -> UserPlan:
        return self._client._get_json("/account/plan", UserPlan)

    def get_entitlements(self) -> dict[str, Any]:
        resp = self._client._get("/account/entitlements")
        return resp.json()

    def get_usage(self) -> UsageTotals:
        return self._client._get_json("/account/usage", UsageTotals)


class AsyncUsersService(AsyncBaseService):
    """Async users service."""

    async def me(self) -> UserProfile:
        """Return the authenticated caller's own profile (GET /user)."""
        return await self._client._get_json("/user", UserProfile)

    async def update(
        self, data: dict[str, Any] | str | int, legacy_data: dict[str, Any] | None = None
    ) -> UserProfile:
        """Update the caller's own profile (PUT /user); returns the updated profile."""
        return await self._client._put_json("/user", _profile_body(data, legacy_data), UserProfile)

    async def get_plan(self) -> UserPlan:
        return await self._client._get_json("/account/plan", UserPlan)

    async def get_entitlements(self) -> dict[str, Any]:
        resp = await self._client._get("/account/entitlements")
        return resp.json()

    async def get_usage(self) -> UsageTotals:
        return await self._client._get_json("/account/usage", UsageTotals)
