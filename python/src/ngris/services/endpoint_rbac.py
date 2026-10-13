from __future__ import annotations

from typing import Any

from ngris.services._base import AsyncBaseService, BaseService, path_id


class EndpointRBACService(BaseService):
    """Sync endpoint RBAC service."""

    def get_rbac(self, uuid: str) -> dict[str, Any]:
        resp = self._client._get(f"/endpoints/{uuid}/rbac")
        return resp.json()

    def list_clients(self, uuid: str) -> list[dict[str, Any]]:
        resp = self._client._get(f"/endpoints/{uuid}/rbac/clients")
        return resp.json()

    def create_client(self, uuid: str, data: dict[str, Any]) -> dict[str, Any]:
        return self._client._post_raw(f"/endpoints/{uuid}/rbac/clients", data)

    def update_client(self, uuid: str, client_uuid: str, data: dict[str, Any]) -> dict[str, Any]:
        return self._client._put_raw(f"/endpoints/{uuid}/rbac/clients/{path_id(client_uuid, 'client_uuid')}", data)

    def delete_client(self, uuid: str, client_uuid: str) -> None:
        self._client._delete_void(f"/endpoints/{uuid}/rbac/clients/{path_id(client_uuid, 'client_uuid')}")

    def list_roles(self, uuid: str) -> list[dict[str, Any]]:
        resp = self._client._get(f"/endpoints/{uuid}/rbac/roles")
        return resp.json()

    def create_role(self, uuid: str, data: dict[str, Any]) -> dict[str, Any]:
        return self._client._post_raw(f"/endpoints/{uuid}/rbac/roles", data)

    def update_role(self, uuid: str, role_uuid: str, data: dict[str, Any]) -> dict[str, Any]:
        return self._client._put_raw(f"/endpoints/{uuid}/rbac/roles/{path_id(role_uuid, 'role_uuid')}", data)

    def delete_role(self, uuid: str, role_uuid: str) -> None:
        self._client._delete_void(f"/endpoints/{uuid}/rbac/roles/{path_id(role_uuid, 'role_uuid')}")

    def list_memberships(self, uuid: str) -> list[dict[str, Any]]:
        resp = self._client._get(f"/endpoints/{uuid}/rbac/memberships")
        return resp.json()

    def create_membership(self, uuid: str, data: dict[str, Any]) -> dict[str, Any]:
        return self._client._post_raw(f"/endpoints/{uuid}/rbac/memberships", data)

    def delete_membership(self, uuid: str, data: dict[str, Any]) -> None:
        self._client._delete_void(f"/endpoints/{uuid}/rbac/memberships", body=data)


class AsyncEndpointRBACService(AsyncBaseService):
    """Async endpoint RBAC service."""

    async def get_rbac(self, uuid: str) -> dict[str, Any]:
        resp = await self._client._get(f"/endpoints/{uuid}/rbac")
        return resp.json()

    async def list_clients(self, uuid: str) -> list[dict[str, Any]]:
        resp = await self._client._get(f"/endpoints/{uuid}/rbac/clients")
        return resp.json()

    async def create_client(self, uuid: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self._client._post_raw(f"/endpoints/{uuid}/rbac/clients", data)

    async def update_client(self, uuid: str, client_uuid: str, data: dict[str, Any]) -> dict[str, Any]:
        client = path_id(client_uuid, "client_uuid")
        return await self._client._put_raw(f"/endpoints/{uuid}/rbac/clients/{client}", data)

    async def delete_client(self, uuid: str, client_uuid: str) -> None:
        await self._client._delete_void(f"/endpoints/{uuid}/rbac/clients/{path_id(client_uuid, 'client_uuid')}")

    async def list_roles(self, uuid: str) -> list[dict[str, Any]]:
        resp = await self._client._get(f"/endpoints/{uuid}/rbac/roles")
        return resp.json()

    async def create_role(self, uuid: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self._client._post_raw(f"/endpoints/{uuid}/rbac/roles", data)

    async def update_role(self, uuid: str, role_uuid: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self._client._put_raw(f"/endpoints/{uuid}/rbac/roles/{path_id(role_uuid, 'role_uuid')}", data)

    async def delete_role(self, uuid: str, role_uuid: str) -> None:
        await self._client._delete_void(f"/endpoints/{uuid}/rbac/roles/{path_id(role_uuid, 'role_uuid')}")

    async def list_memberships(self, uuid: str) -> list[dict[str, Any]]:
        resp = await self._client._get(f"/endpoints/{uuid}/rbac/memberships")
        return resp.json()

    async def create_membership(self, uuid: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self._client._post_raw(f"/endpoints/{uuid}/rbac/memberships", data)

    async def delete_membership(self, uuid: str, data: dict[str, Any]) -> None:
        await self._client._delete_void(f"/endpoints/{uuid}/rbac/memberships", body=data)
