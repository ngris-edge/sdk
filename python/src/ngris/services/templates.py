from __future__ import annotations

from typing import Any

from ngris.models.templates import CustomTemplate
from ngris.services._base import AsyncBaseService, BaseService, path_id


class TemplatesService(BaseService):
    """Sync custom templates service."""

    def list(self) -> list[dict[str, Any]]:
        resp = self._client._get("/templates")
        return resp.json()

    def upload(self, data: dict[str, Any]) -> CustomTemplate:
        return self._client._post_json("/templates", data, CustomTemplate)

    def delete(self, template_uuid: str) -> None:
        self._client._delete_void(f"/templates/{path_id(template_uuid, 'template_uuid')}")

    def activate(self, template_uuid: str, type: str) -> None:
        """Make this template the active one for its ``type`` (e.g. ``"firewall"``).

        The API requires the type in the body and answers 200 with no body.
        """
        template = path_id(template_uuid, "template_uuid")
        self._client._post_void(f"/templates/{template}/activate", {"type": type})


class AsyncTemplatesService(AsyncBaseService):
    """Async custom templates service."""

    async def list(self) -> list[dict[str, Any]]:
        resp = await self._client._get("/templates")
        return resp.json()

    async def upload(self, data: dict[str, Any]) -> CustomTemplate:
        return await self._client._post_json("/templates", data, CustomTemplate)

    async def delete(self, template_uuid: str) -> None:
        await self._client._delete_void(f"/templates/{path_id(template_uuid, 'template_uuid')}")

    async def activate(self, template_uuid: str, type: str) -> None:
        template = path_id(template_uuid, "template_uuid")
        await self._client._post_void(f"/templates/{template}/activate", {"type": type})
