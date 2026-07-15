from __future__ import annotations

from typing import Any

from ngris.models.sso import SSOConfig
from ngris.services._base import AsyncBaseService, BaseService


class SSOService(BaseService):
    """Sync SSO service."""

    def list(self) -> list[dict[str, Any]]:
        resp = self._client._get("/sso/config")
        return resp.json()

    def create(self, data: dict[str, Any]) -> SSOConfig:
        return self._client._post_json("/sso/config", data, SSOConfig)

    def get(self, config_id: str) -> SSOConfig:
        return self._client._get_json(f"/sso/config/{config_id}", SSOConfig)

    def update(self, config_id: str, data: dict[str, Any]) -> SSOConfig:
        return self._client._put_json(f"/sso/config/{config_id}", data, SSOConfig)

    def delete(self, config_id: str) -> None:
        self._client._delete_void(f"/sso/config/{config_id}")

    def test(self, config_id: str) -> dict[str, Any]:
        return self._client._post_raw(f"/sso/config/{config_id}/test", {})


class AsyncSSOService(AsyncBaseService):
    """Async SSO service."""

    async def list(self) -> list[dict[str, Any]]:
        resp = await self._client._get("/sso/config")
        return resp.json()

    async def create(self, data: dict[str, Any]) -> SSOConfig:
        return await self._client._post_json("/sso/config", data, SSOConfig)

    async def get(self, config_id: str) -> SSOConfig:
        return await self._client._get_json(f"/sso/config/{config_id}", SSOConfig)

    async def update(self, config_id: str, data: dict[str, Any]) -> SSOConfig:
        return await self._client._put_json(f"/sso/config/{config_id}", data, SSOConfig)

    async def delete(self, config_id: str) -> None:
        await self._client._delete_void(f"/sso/config/{config_id}")

    async def test(self, config_id: str) -> dict[str, Any]:
        return await self._client._post_raw(f"/sso/config/{config_id}/test", {})
