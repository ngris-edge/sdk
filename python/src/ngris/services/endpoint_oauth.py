from __future__ import annotations

from typing import Any

from ngris.services._base import AsyncBaseService, BaseService


class EndpointOAuthService(BaseService):
    """Sync endpoint OAuth service."""

    def list_providers(self, endpoint_id: str) -> list[dict[str, Any]]:
        resp = self._client._get(f"/endpoints/{endpoint_id}/oauth/providers")
        return resp.json()

    def create_provider(self, endpoint_id: str, data: dict[str, Any]) -> dict[str, Any]:
        return self._client._post_raw(f"/endpoints/{endpoint_id}/oauth/providers", data)

    def get_provider(self, endpoint_id: str, provider_id: str) -> dict[str, Any]:
        return self._client._get_raw(f"/endpoints/{endpoint_id}/oauth/providers/{provider_id}")

    def update_provider(self, endpoint_id: str, provider_id: str, data: dict[str, Any]) -> dict[str, Any]:
        return self._client._put_raw(
            f"/endpoints/{endpoint_id}/oauth/providers/{provider_id}", data
        )

    def delete_provider(self, endpoint_id: str, provider_id: str) -> None:
        self._client._delete_void(f"/endpoints/{endpoint_id}/oauth/providers/{provider_id}")

    def toggle_provider(self, endpoint_id: str, provider_id: str) -> dict[str, Any]:
        return self._client._put_raw(
            f"/endpoints/{endpoint_id}/oauth/providers/{provider_id}/toggle", {}
        )

    def get_presets(self) -> list[dict[str, Any]]:
        resp = self._client._get("/oauth/presets")
        return resp.json()


class AsyncEndpointOAuthService(AsyncBaseService):
    """Async endpoint OAuth service."""

    async def list_providers(self, endpoint_id: str) -> list[dict[str, Any]]:
        resp = await self._client._get(f"/endpoints/{endpoint_id}/oauth/providers")
        return resp.json()

    async def create_provider(self, endpoint_id: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self._client._post_raw(f"/endpoints/{endpoint_id}/oauth/providers", data)

    async def get_provider(self, endpoint_id: str, provider_id: str) -> dict[str, Any]:
        return await self._client._get_raw(f"/endpoints/{endpoint_id}/oauth/providers/{provider_id}")

    async def update_provider(self, endpoint_id: str, provider_id: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self._client._put_raw(
            f"/endpoints/{endpoint_id}/oauth/providers/{provider_id}", data
        )

    async def delete_provider(self, endpoint_id: str, provider_id: str) -> None:
        await self._client._delete_void(f"/endpoints/{endpoint_id}/oauth/providers/{provider_id}")

    async def toggle_provider(self, endpoint_id: str, provider_id: str) -> dict[str, Any]:
        return await self._client._put_raw(
            f"/endpoints/{endpoint_id}/oauth/providers/{provider_id}/toggle", {}
        )

    async def get_presets(self) -> list[dict[str, Any]]:
        resp = await self._client._get("/oauth/presets")
        return resp.json()
