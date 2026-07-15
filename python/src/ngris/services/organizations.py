from __future__ import annotations

from typing import Any

from ngris.models.organizations import Organization
from ngris.services._base import AsyncBaseService, BaseService


class OrganizationsService(BaseService):
    """Sync organizations service."""

    def list(self) -> list[dict[str, Any]]:
        resp = self._client._get("/organizations")
        return resp.json()

    def create(self, data: dict[str, Any]) -> Organization:
        return self._client._post_json("/organization", data, Organization)

    def get(self, org_id: str) -> Organization:
        return self._client._get_json(f"/organization/{org_id}", Organization)

    def update(self, org_id: str, data: dict[str, Any]) -> Organization:
        return self._client._put_json(f"/organization/{org_id}", data, Organization)

    def delete(self, org_id: str) -> None:
        self._client._delete_void(f"/organization/{org_id}")

    def list_members(self, org_id: str) -> list[dict[str, Any]]:
        resp = self._client._get(f"/organization/{org_id}/members")
        return resp.json()

    def invite_member(self, org_id: str, data: dict[str, Any]) -> dict[str, Any]:
        return self._client._post_raw(f"/organization/{org_id}/members/invite", data)

    def remove_member(self, org_id: str, user_id: str) -> None:
        self._client._post_void(f"/organization/{org_id}/members/remove", {"user_id": user_id})

    def switch(self, org_id: str) -> None:
        self._client._post_void("/organization/switch", {"org_id": org_id})


class AsyncOrganizationsService(AsyncBaseService):
    """Async organizations service."""

    async def list(self) -> list[dict[str, Any]]:
        resp = await self._client._get("/organizations")
        return resp.json()

    async def create(self, data: dict[str, Any]) -> Organization:
        return await self._client._post_json("/organization", data, Organization)

    async def get(self, org_id: str) -> Organization:
        return await self._client._get_json(f"/organization/{org_id}", Organization)

    async def update(self, org_id: str, data: dict[str, Any]) -> Organization:
        return await self._client._put_json(f"/organization/{org_id}", data, Organization)

    async def delete(self, org_id: str) -> None:
        await self._client._delete_void(f"/organization/{org_id}")

    async def list_members(self, org_id: str) -> list[dict[str, Any]]:
        resp = await self._client._get(f"/organization/{org_id}/members")
        return resp.json()

    async def invite_member(self, org_id: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self._client._post_raw(f"/organization/{org_id}/members/invite", data)

    async def remove_member(self, org_id: str, user_id: str) -> None:
        await self._client._post_void(f"/organization/{org_id}/members/remove", {"user_id": user_id})

    async def switch(self, org_id: str) -> None:
        await self._client._post_void("/organization/switch", {"org_id": org_id})
