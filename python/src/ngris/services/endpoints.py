from __future__ import annotations

from typing import Any, AsyncIterator, Iterator

from ngris._pagination import AsyncPageIterator, PaginatedResponse
from ngris.models.endpoints import Endpoint, EndpointAuthSettings, HealthStatus
from ngris.services._base import AsyncBaseService, BaseService


class EndpointsService(BaseService):
    """Sync endpoints service."""

    def list(self, page: int = 1, page_size: int = 50) -> PaginatedResponse[Endpoint]:
        return self._client._get_page("/endpoints", Endpoint, page=page, page_size=page_size)

    def list_all(self) -> Iterator[Endpoint]:
        return self._client._autopage("/endpoints", Endpoint)

    def create(self, data: dict[str, Any]) -> Endpoint:
        return self._client._post_json("/endpoints", data, Endpoint)

    def get(self, uuid: str) -> Endpoint:
        return self._client._get_json(f"/endpoints/{uuid}", Endpoint)

    def delete(self, uuid: str) -> None:
        self._client._delete_void(f"/endpoints/{uuid}")

    def assign_certificate(
        self, uuid: str, certificate_id: int | None = None, *, use_default: bool = False
    ) -> None:
        """Attach a custom certificate to an endpoint, or revert to the default.

        Pass ``use_default=True`` (or ``certificate_id=None``) to remove any
        custom certificate and fall back to the auto-managed cert.
        """
        body: dict[str, Any] = {"use_default": use_default}
        if certificate_id is not None:
            body["certificate_id"] = certificate_id
        self._client._put_void(f"/endpoints/{uuid}/certificate", body)

    def get_settings(self, uuid: str) -> EndpointAuthSettings:
        return self._client._get_json(f"/endpoints/{uuid}/settings", EndpointAuthSettings)

    def update_settings(self, uuid: str, data: dict[str, Any]) -> None:
        self._client._put_void(f"/endpoints/{uuid}/settings", data)

    def get_health(self, uuid: str) -> HealthStatus:
        return self._client._get_json(f"/endpoints/{uuid}/health", HealthStatus)

    def promote(self, uuid: str) -> Endpoint:
        return self._client._post_json(f"/endpoints/{uuid}/promote", {}, Endpoint)


class AsyncEndpointsService(AsyncBaseService):
    """Async endpoints service."""

    async def list(self, page: int = 1, page_size: int = 50) -> PaginatedResponse[Endpoint]:
        return await self._client._get_page("/endpoints", Endpoint, page=page, page_size=page_size)

    def list_all(self) -> AsyncPageIterator[Endpoint]:
        return self._client._autopage("/endpoints", Endpoint)

    async def create(self, data: dict[str, Any]) -> Endpoint:
        return await self._client._post_json("/endpoints", data, Endpoint)

    async def get(self, uuid: str) -> Endpoint:
        return await self._client._get_json(f"/endpoints/{uuid}", Endpoint)

    async def delete(self, uuid: str) -> None:
        await self._client._delete_void(f"/endpoints/{uuid}")

    async def assign_certificate(
        self, uuid: str, certificate_id: int | None = None, *, use_default: bool = False
    ) -> None:
        body: dict[str, Any] = {"use_default": use_default}
        if certificate_id is not None:
            body["certificate_id"] = certificate_id
        await self._client._put_void(f"/endpoints/{uuid}/certificate", body)

    async def get_settings(self, uuid: str) -> EndpointAuthSettings:
        return await self._client._get_json(f"/endpoints/{uuid}/settings", EndpointAuthSettings)

    async def update_settings(self, uuid: str, data: dict[str, Any]) -> None:
        await self._client._put_void(f"/endpoints/{uuid}/settings", data)

    async def get_health(self, uuid: str) -> HealthStatus:
        return await self._client._get_json(f"/endpoints/{uuid}/health", HealthStatus)

    async def promote(self, uuid: str) -> Endpoint:
        return await self._client._post_json(f"/endpoints/{uuid}/promote", {}, Endpoint)
