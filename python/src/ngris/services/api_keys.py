from __future__ import annotations

from typing import Any

from ngris.services._base import AsyncBaseService, BaseService, path_id, put_ref, renamed_kwarg


def _auth_token_body(
    description: str,
    endpoint_uuid: str | None,
    tunnel_uuid: str | None,
    endpoint_id: str | int | None,
) -> dict[str, Any]:
    body: dict[str, Any] = {"description": description}
    endpoint = renamed_kwarg(endpoint_uuid, endpoint_id, "endpoint_id", "endpoint_uuid", _extra=1)
    put_ref(body, "endpoint", endpoint, _extra=1)
    put_ref(body, "tunnel", tunnel_uuid, _extra=1)
    return body


class APIKeysService(BaseService):
    """Sync API keys service."""

    def list_api_keys(self) -> list[dict[str, Any]]:
        resp = self._client._get("/keys/api")
        return resp.json()

    def create_api_key(self, description: str = "") -> dict[str, Any]:
        """Create an API key. The response carries the key's ``uuid``."""
        return self._client._post_raw("/keys/api", {"description": description})

    def delete_api_key(self, key_uuid: str) -> None:
        self._client._delete_void(f"/keys/api/{path_id(key_uuid, 'key_uuid')}")

    def list_auth_tokens(self) -> list[dict[str, Any]]:
        resp = self._client._get("/keys/auth")
        return resp.json()

    def create_auth_token(
        self,
        description: str = "",
        endpoint_uuid: str | None = None,
        *,
        tunnel_uuid: str | None = None,
        endpoint_id: str | int | None = None,
    ) -> dict[str, Any]:
        """Mint an agent auth token, optionally bound to one endpoint or tunnel.

        The response carries the token's ``uuid`` (use it to revoke the token)
        and the ``token`` secret. ``endpoint_id=`` is the deprecated name of
        ``endpoint_uuid=``.
        """
        body = _auth_token_body(description, endpoint_uuid, tunnel_uuid, endpoint_id)
        return self._client._post_raw("/keys/auth", body)

    def delete_auth_token(self, token_uuid: str) -> None:
        self._client._delete_void(f"/keys/auth/{path_id(token_uuid, 'token_uuid')}")


class AsyncAPIKeysService(AsyncBaseService):
    """Async API keys service."""

    async def list_api_keys(self) -> list[dict[str, Any]]:
        resp = await self._client._get("/keys/api")
        return resp.json()

    async def create_api_key(self, description: str = "") -> dict[str, Any]:
        return await self._client._post_raw("/keys/api", {"description": description})

    async def delete_api_key(self, key_uuid: str) -> None:
        await self._client._delete_void(f"/keys/api/{path_id(key_uuid, 'key_uuid')}")

    async def list_auth_tokens(self) -> list[dict[str, Any]]:
        resp = await self._client._get("/keys/auth")
        return resp.json()

    async def create_auth_token(
        self,
        description: str = "",
        endpoint_uuid: str | None = None,
        *,
        tunnel_uuid: str | None = None,
        endpoint_id: str | int | None = None,
    ) -> dict[str, Any]:
        body = _auth_token_body(description, endpoint_uuid, tunnel_uuid, endpoint_id)
        return await self._client._post_raw("/keys/auth", body)

    async def delete_auth_token(self, token_uuid: str) -> None:
        await self._client._delete_void(f"/keys/auth/{path_id(token_uuid, 'token_uuid')}")
