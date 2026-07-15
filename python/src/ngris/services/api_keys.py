from __future__ import annotations

from typing import Any

from ngris.services._base import AsyncBaseService, BaseService


class APIKeysService(BaseService):
    """Sync API keys service."""

    def list_api_keys(self) -> list[dict[str, Any]]:
        resp = self._client._get("/keys/api")
        return resp.json()

    def create_api_key(self, description: str = "") -> dict[str, Any]:
        return self._client._post_raw("/keys/api", {"description": description})

    def delete_api_key(self, key_id: str) -> None:
        self._client._delete_void(f"/keys/api/{key_id}")

    def list_auth_tokens(self) -> list[dict[str, Any]]:
        resp = self._client._get("/keys/auth")
        return resp.json()

    def create_auth_token(self, description: str = "", endpoint_id: str | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {"description": description}
        if endpoint_id is not None:
            body["endpoint_id"] = endpoint_id
        return self._client._post_raw("/keys/auth", body)

    def delete_auth_token(self, token_id: str | int) -> None:
        self._client._delete_void(f"/keys/auth/{token_id}")


class AsyncAPIKeysService(AsyncBaseService):
    """Async API keys service."""

    async def list_api_keys(self) -> list[dict[str, Any]]:
        resp = await self._client._get("/keys/api")
        return resp.json()

    async def create_api_key(self, description: str = "") -> dict[str, Any]:
        return await self._client._post_raw("/keys/api", {"description": description})

    async def delete_api_key(self, key_id: str) -> None:
        await self._client._delete_void(f"/keys/api/{key_id}")

    async def list_auth_tokens(self) -> list[dict[str, Any]]:
        resp = await self._client._get("/keys/auth")
        return resp.json()

    async def create_auth_token(self, description: str = "", endpoint_id: str | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {"description": description}
        if endpoint_id is not None:
            body["endpoint_id"] = endpoint_id
        return await self._client._post_raw("/keys/auth", body)

    async def delete_auth_token(self, token_id: str | int) -> None:
        await self._client._delete_void(f"/keys/auth/{token_id}")
