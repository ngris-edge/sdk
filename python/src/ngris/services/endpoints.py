from __future__ import annotations

from typing import Any, AsyncIterator, Iterator

from ngris._pagination import AsyncPageIterator, PaginatedResponse
from ngris.models.endpoints import Endpoint, EndpointAuthSettings, HealthStatus
from ngris.services._base import AsyncBaseService, BaseService, put_ref, renamed_kwarg


def _certificate_body(
    certificate_uuid: str | None, certificate_id: int | None, use_default: bool
) -> dict[str, Any]:
    body: dict[str, Any] = {"use_default": use_default}
    certificate = renamed_kwarg(certificate_uuid, certificate_id, "certificate_id", "certificate_uuid", _extra=1)
    put_ref(body, "certificate", certificate, _extra=1)
    return body


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
        self,
        uuid: str,
        certificate_uuid: str | None = None,
        *,
        use_default: bool = False,
        certificate_id: int | None = None,
    ) -> None:
        """Attach a custom certificate (by its ``uuid``) to an endpoint, or revert to the default.

        Pass ``use_default=True`` (or no certificate) to remove any custom
        certificate and fall back to the auto-managed cert. ``certificate_id=``
        (an integer id) is deprecated and accepted until the API's integer-id
        sunset.
        """
        body = _certificate_body(certificate_uuid, certificate_id, use_default)
        self._client._put_void(f"/endpoints/{uuid}/certificate", body)

    def get_settings(self, uuid: str) -> EndpointAuthSettings:
        return self._client._get_json(f"/endpoints/{uuid}/settings", EndpointAuthSettings)

    def update_settings(self, uuid: str, data: dict[str, Any]) -> None:
        self._client._put_void(f"/endpoints/{uuid}/settings", data)

    def get_health(self, uuid: str) -> HealthStatus:
        return self._client._get_json(f"/endpoints/{uuid}/health", HealthStatus)

    def promote(self, uuid: str) -> dict[str, Any]:
        """Promote an ephemeral endpoint to permanent.

        The API answers a minimal confirmation (``uuid``, ``endpoint_uuid``,
        ``ephemeral``), not the full endpoint; call :meth:`get` for that.
        """
        return self._client._post_raw(f"/endpoints/{uuid}/promote", {})


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
        self,
        uuid: str,
        certificate_uuid: str | None = None,
        *,
        use_default: bool = False,
        certificate_id: int | None = None,
    ) -> None:
        body = _certificate_body(certificate_uuid, certificate_id, use_default)
        await self._client._put_void(f"/endpoints/{uuid}/certificate", body)

    async def get_settings(self, uuid: str) -> EndpointAuthSettings:
        return await self._client._get_json(f"/endpoints/{uuid}/settings", EndpointAuthSettings)

    async def update_settings(self, uuid: str, data: dict[str, Any]) -> None:
        await self._client._put_void(f"/endpoints/{uuid}/settings", data)

    async def get_health(self, uuid: str) -> HealthStatus:
        return await self._client._get_json(f"/endpoints/{uuid}/health", HealthStatus)

    async def promote(self, uuid: str) -> dict[str, Any]:
        return await self._client._post_raw(f"/endpoints/{uuid}/promote", {})
