from __future__ import annotations

from typing import Any

from ngris.models.domains import Domain
from ngris.services._base import AsyncBaseService, BaseService


class DomainsService(BaseService):
    """Sync domains service."""

    def list_available(self) -> list[dict[str, Any]]:
        resp = self._client._get("/domains/available")
        return resp.json()

    def create(self, data: dict[str, Any]) -> Domain:
        return self._client._post_json("/domains/self", data, Domain)

    def update(self, uuid: str, data: dict[str, Any]) -> Domain:
        return self._client._put_json(f"/domains/self/{uuid}", data, Domain)

    def delete(self, uuid: str) -> None:
        self._client._delete_void(f"/domains/self/{uuid}")

    def get_acme_status(self, uuid: str) -> dict[str, Any]:
        resp = self._client._get(f"/domains/self/{uuid}/acme/status")
        return resp.json()

    def reissue_ssl(self, uuid: str) -> dict[str, Any]:
        return self._client._post_raw(f"/domains/self/{uuid}/reissue-ssl", {})

    def list_dns_records(self, uuid: str) -> list[dict[str, Any]]:
        resp = self._client._get(f"/domains/self/{uuid}/dns-records")
        return resp.json()

    def create_dns_record(self, uuid: str, data: dict[str, Any]) -> dict[str, Any]:
        return self._client._post_raw(f"/domains/self/{uuid}/dns-records", data)

    def update_dns_record(self, uuid: str, record_id: str, data: dict[str, Any]) -> dict[str, Any]:
        return self._client._put_raw(f"/domains/self/{uuid}/dns-records/{record_id}", data)

    def delete_dns_record(self, uuid: str, record_id: str) -> None:
        self._client._delete_void(f"/domains/self/{uuid}/dns-records/{record_id}")


class AsyncDomainsService(AsyncBaseService):
    """Async domains service."""

    async def list_available(self) -> list[dict[str, Any]]:
        resp = await self._client._get("/domains/available")
        return resp.json()

    async def create(self, data: dict[str, Any]) -> Domain:
        return await self._client._post_json("/domains/self", data, Domain)

    async def update(self, uuid: str, data: dict[str, Any]) -> Domain:
        return await self._client._put_json(f"/domains/self/{uuid}", data, Domain)

    async def delete(self, uuid: str) -> None:
        await self._client._delete_void(f"/domains/self/{uuid}")

    async def get_acme_status(self, uuid: str) -> dict[str, Any]:
        resp = await self._client._get(f"/domains/self/{uuid}/acme/status")
        return resp.json()

    async def reissue_ssl(self, uuid: str) -> dict[str, Any]:
        return await self._client._post_raw(f"/domains/self/{uuid}/reissue-ssl", {})

    async def list_dns_records(self, uuid: str) -> list[dict[str, Any]]:
        resp = await self._client._get(f"/domains/self/{uuid}/dns-records")
        return resp.json()

    async def create_dns_record(self, uuid: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self._client._post_raw(f"/domains/self/{uuid}/dns-records", data)

    async def update_dns_record(self, uuid: str, record_id: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self._client._put_raw(f"/domains/self/{uuid}/dns-records/{record_id}", data)

    async def delete_dns_record(self, uuid: str, record_id: str) -> None:
        await self._client._delete_void(f"/domains/self/{uuid}/dns-records/{record_id}")
