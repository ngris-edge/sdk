from __future__ import annotations

from typing import Any

from ngris.models.templates import CustomTemplate
from ngris.services._base import AsyncBaseService, BaseService, path_id


def _upload_parts(
    type: str, content: str | bytes, active: bool
) -> tuple[dict[str, str], dict[str, tuple[str, bytes, str]]]:
    """The multipart form ``POST /templates`` reads: the page as the
    ``template`` file part, its ``type``, and ``active=true`` when set."""
    page = content.encode("utf-8") if isinstance(content, str) else bytes(content)
    form = {"type": type}
    if active:
        form["active"] = "true"
    return form, {"template": ("template.html", page, "text/html")}


class TemplatesService(BaseService):
    """Sync custom templates service."""

    def list(self) -> list[dict[str, Any]]:
        resp = self._client._get("/templates")
        return resp.json()

    def upload(self, type: str, content: str | bytes, *, active: bool = False) -> CustomTemplate:
        """Upload a custom error page (HTML) for ``type``.

        ``type`` is one of ``firewall``, ``rate_limit``, ``bad_gateway``,
        ``service_unavailable``, ``not_found``, ``request_timeout``,
        ``internal_error``, ``gateway_timeout``. The page is sent as
        multipart/form-data. The API scans it for unsafe content before
        saving: a page that fails the scan is a 400 with the reason.

        ``active=True`` saves the page as active. It does not deactivate the
        account's other page of the same type; :meth:`activate` does.
        """
        form, files = _upload_parts(type, content, active)
        resp = self._client._post("/templates", form=form, files=files)
        template: CustomTemplate = self._client._parse_response(resp, CustomTemplate)
        return template

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

    async def upload(self, type: str, content: str | bytes, *, active: bool = False) -> CustomTemplate:
        form, files = _upload_parts(type, content, active)
        resp = await self._client._post("/templates", form=form, files=files)
        template: CustomTemplate = self._client._parse_response(resp, CustomTemplate)
        return template

    async def delete(self, template_uuid: str) -> None:
        await self._client._delete_void(f"/templates/{path_id(template_uuid, 'template_uuid')}")

    async def activate(self, template_uuid: str, type: str) -> None:
        template = path_id(template_uuid, "template_uuid")
        await self._client._post_void(f"/templates/{template}/activate", {"type": type})
