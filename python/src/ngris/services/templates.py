from __future__ import annotations

from typing import Any

from ngris.models.templates import CustomTemplate
from ngris.services._base import AsyncBaseService, BaseService


class TemplatesService(BaseService):
    """Sync custom templates service."""

    def list(self) -> list[dict[str, Any]]:
        resp = self._client._get("/templates")
        return resp.json()

    def upload(self, data: dict[str, Any]) -> CustomTemplate:
        return self._client._post_json("/templates", data, CustomTemplate)

    def delete(self, template_id: str) -> None:
        self._client._delete_void(f"/templates/{template_id}")

    def activate(self, template_id: str) -> CustomTemplate:
        return self._client._post_json(f"/templates/{template_id}/activate", {}, CustomTemplate)


class AsyncTemplatesService(AsyncBaseService):
    """Async custom templates service."""

    async def list(self) -> list[dict[str, Any]]:
        resp = await self._client._get("/templates")
        return resp.json()

    async def upload(self, data: dict[str, Any]) -> CustomTemplate:
        return await self._client._post_json("/templates", data, CustomTemplate)

    async def delete(self, template_id: str) -> None:
        await self._client._delete_void(f"/templates/{template_id}")

    async def activate(self, template_id: str) -> CustomTemplate:
        return await self._client._post_json(f"/templates/{template_id}/activate", {}, CustomTemplate)
