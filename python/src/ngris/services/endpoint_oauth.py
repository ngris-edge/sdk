from __future__ import annotations

from typing import Any

from ngris.services._base import AsyncBaseService, BaseService, path_id


class EndpointOAuthService(BaseService):
    """Sync endpoint OAuth service."""

    def list_providers(self, endpoint_uuid: str) -> list[dict[str, Any]]:
        resp = self._client._get(f"/endpoints/{endpoint_uuid}/oauth/providers")
        return resp.json()

    def create_provider(self, endpoint_uuid: str, data: dict[str, Any]) -> dict[str, Any]:
        return self._client._post_raw(f"/endpoints/{endpoint_uuid}/oauth/providers", data)

    def get_provider(self, endpoint_uuid: str, provider_uuid: str) -> dict[str, Any]:
        provider = path_id(provider_uuid, "provider_uuid")
        return self._client._get_raw(f"/endpoints/{endpoint_uuid}/oauth/providers/{provider}")

    def update_provider(self, endpoint_uuid: str, provider_uuid: str, data: dict[str, Any]) -> dict[str, Any]:
        return self._client._put_raw(
            f"/endpoints/{endpoint_uuid}/oauth/providers/{path_id(provider_uuid, 'provider_uuid')}", data
        )

    def delete_provider(self, endpoint_uuid: str, provider_uuid: str) -> None:
        provider = path_id(provider_uuid, "provider_uuid")
        self._client._delete_void(f"/endpoints/{endpoint_uuid}/oauth/providers/{provider}")

    def toggle_provider(self, endpoint_uuid: str, provider_uuid: str) -> dict[str, Any]:
        return self._client._put_raw(
            f"/endpoints/{endpoint_uuid}/oauth/providers/{path_id(provider_uuid, 'provider_uuid')}/toggle", {}
        )

    def get_presets(self) -> list[dict[str, Any]]:
        resp = self._client._get("/oauth/presets")
        return resp.json()


class AsyncEndpointOAuthService(AsyncBaseService):
    """Async endpoint OAuth service."""

    async def list_providers(self, endpoint_uuid: str) -> list[dict[str, Any]]:
        resp = await self._client._get(f"/endpoints/{endpoint_uuid}/oauth/providers")
        return resp.json()

    async def create_provider(self, endpoint_uuid: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self._client._post_raw(f"/endpoints/{endpoint_uuid}/oauth/providers", data)

    async def get_provider(self, endpoint_uuid: str, provider_uuid: str) -> dict[str, Any]:
        provider = path_id(provider_uuid, "provider_uuid")
        return await self._client._get_raw(f"/endpoints/{endpoint_uuid}/oauth/providers/{provider}")

    async def update_provider(self, endpoint_uuid: str, provider_uuid: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self._client._put_raw(
            f"/endpoints/{endpoint_uuid}/oauth/providers/{path_id(provider_uuid, 'provider_uuid')}", data
        )

    async def delete_provider(self, endpoint_uuid: str, provider_uuid: str) -> None:
        provider = path_id(provider_uuid, "provider_uuid")
        await self._client._delete_void(f"/endpoints/{endpoint_uuid}/oauth/providers/{provider}")

    async def toggle_provider(self, endpoint_uuid: str, provider_uuid: str) -> dict[str, Any]:
        return await self._client._put_raw(
            f"/endpoints/{endpoint_uuid}/oauth/providers/{path_id(provider_uuid, 'provider_uuid')}/toggle", {}
        )

    async def get_presets(self) -> list[dict[str, Any]]:
        resp = await self._client._get("/oauth/presets")
        return resp.json()
