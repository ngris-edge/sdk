from __future__ import annotations

from typing import Any

from ngris.models.certificates import Certificate
from ngris.services._base import AsyncBaseService, BaseService


class CertificatesService(BaseService):
    """Sync certificates service."""

    def list(self) -> list[dict[str, Any]]:
        resp = self._client._get("/certificates/self")
        return resp.json()

    def upload(self, data: dict[str, Any]) -> Certificate:
        return self._client._post_json("/certificates/self", data, Certificate)

    def delete(self, uuid: str) -> None:
        self._client._delete_void(f"/certificates/self/{uuid}")

    def download(self, uuid: str) -> bytes:
        resp = self._client._get(f"/certificates/self/{uuid}/download")
        return resp.content


class AsyncCertificatesService(AsyncBaseService):
    """Async certificates service."""

    async def list(self) -> list[dict[str, Any]]:
        resp = await self._client._get("/certificates/self")
        return resp.json()

    async def upload(self, data: dict[str, Any]) -> Certificate:
        return await self._client._post_json("/certificates/self", data, Certificate)

    async def delete(self, uuid: str) -> None:
        await self._client._delete_void(f"/certificates/self/{uuid}")

    async def download(self, uuid: str) -> bytes:
        resp = await self._client._get(f"/certificates/self/{uuid}/download")
        return resp.content
