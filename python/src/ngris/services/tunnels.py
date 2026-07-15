from __future__ import annotations

from typing import Any

from ngris.models.tunnels import Tunnel
from ngris.services._base import AsyncBaseService, BaseService


class TunnelsService(BaseService):
    """Sync tunnels service."""

    def list(self) -> list[dict[str, Any]]:
        resp = self._client._get("/tunnels")
        return resp.json()

    def get(self, tunnel_id: str) -> Tunnel:
        return self._client._get_json(f"/tunnels/{tunnel_id}", Tunnel)


class AsyncTunnelsService(AsyncBaseService):
    """Async tunnels service."""

    async def list(self) -> list[dict[str, Any]]:
        resp = await self._client._get("/tunnels")
        return resp.json()

    async def get(self, tunnel_id: str) -> Tunnel:
        return await self._client._get_json(f"/tunnels/{tunnel_id}", Tunnel)
