from __future__ import annotations

from typing import Any

from ngris.models.client_cas import ClientCA, MTLSConfig
from ngris.services._base import AsyncBaseService, BaseService


class ClientCAsService(BaseService):
    """Sync client CAs service."""

    def list(self) -> list[dict[str, Any]]:
        resp = self._client._get("/client-cas")
        return resp.json()

    def create(self, data: dict[str, Any]) -> ClientCA:
        return self._client._post_json("/client-cas", data, ClientCA)

    def get(self, ca_id: str) -> ClientCA:
        return self._client._get_json(f"/client-cas/{ca_id}", ClientCA)

    def delete(self, ca_id: str) -> None:
        self._client._delete_void(f"/client-cas/{ca_id}")

    def get_mtls(self, endpoint_uuid: str) -> MTLSConfig:
        return self._client._get_json(f"/endpoints/{endpoint_uuid}/mtls", MTLSConfig)

    def update_mtls(self, endpoint_uuid: str, data: dict[str, Any]) -> None:
        self._client._put_void(f"/endpoints/{endpoint_uuid}/mtls", data)


class AsyncClientCAsService(AsyncBaseService):
    """Async client CAs service."""

    async def list(self) -> list[dict[str, Any]]:
        resp = await self._client._get("/client-cas")
        return resp.json()

    async def create(self, data: dict[str, Any]) -> ClientCA:
        return await self._client._post_json("/client-cas", data, ClientCA)

    async def get(self, ca_id: str) -> ClientCA:
        return await self._client._get_json(f"/client-cas/{ca_id}", ClientCA)

    async def delete(self, ca_id: str) -> None:
        await self._client._delete_void(f"/client-cas/{ca_id}")

    async def get_mtls(self, endpoint_uuid: str) -> MTLSConfig:
        return await self._client._get_json(f"/endpoints/{endpoint_uuid}/mtls", MTLSConfig)

    async def update_mtls(self, endpoint_uuid: str, data: dict[str, Any]) -> None:
        await self._client._put_void(f"/endpoints/{endpoint_uuid}/mtls", data)
