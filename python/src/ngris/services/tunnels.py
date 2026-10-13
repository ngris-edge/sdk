from __future__ import annotations

from typing import Any

from ngris.models.tunnels import Tunnel
from ngris.services._base import AsyncBaseService, BaseService, path_id


class TunnelsService(BaseService):
    """Sync tunnels service."""

    def list(self) -> list[dict[str, Any]]:
        resp = self._client._get("/tunnels")
        return resp.json()

    def get(self, tunnel_uuid: str) -> Tunnel:
        return self._client._get_json(f"/tunnels/{path_id(tunnel_uuid, 'tunnel_uuid')}", Tunnel)


class AsyncTunnelsService(AsyncBaseService):
    """Async tunnels service."""

    async def list(self) -> list[dict[str, Any]]:
        resp = await self._client._get("/tunnels")
        return resp.json()

    async def get(self, tunnel_uuid: str) -> Tunnel:
        return await self._client._get_json(f"/tunnels/{path_id(tunnel_uuid, 'tunnel_uuid')}", Tunnel)
