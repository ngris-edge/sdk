from __future__ import annotations

from typing import Any

from ngris.services._base import AsyncBaseService, BaseService


class SupportService(BaseService):
    """Sync support service."""

    def list_tickets(self) -> list[dict[str, Any]]:
        resp = self._client._get("/support/tickets")
        return resp.json()

    def create_ticket(self, data: dict[str, Any]) -> dict[str, Any]:
        return self._client._post_raw("/support/tickets", data)

    def get_ticket(self, uuid: str) -> dict[str, Any]:
        return self._client._get_raw(f"/support/tickets/{uuid}")

    def reply(self, uuid: str, message: str) -> dict[str, Any]:
        return self._client._post_raw(
            f"/support/tickets/{uuid}/messages",
            {"message": message},
        )

    def close_ticket(self, uuid: str) -> None:
        self._client._post_void(f"/support/tickets/{uuid}/close", {})

    def rate_ticket(self, uuid: str, rating: int, comment: str | None = None) -> None:
        body: dict[str, Any] = {"rating": rating}
        if comment is not None:
            body["comment"] = comment
        self._client._post_void(f"/support/tickets/{uuid}/rate", body)


class AsyncSupportService(AsyncBaseService):
    """Async support service."""

    async def list_tickets(self) -> list[dict[str, Any]]:
        resp = await self._client._get("/support/tickets")
        return resp.json()

    async def create_ticket(self, data: dict[str, Any]) -> dict[str, Any]:
        return await self._client._post_raw("/support/tickets", data)

    async def get_ticket(self, uuid: str) -> dict[str, Any]:
        return await self._client._get_raw(f"/support/tickets/{uuid}")

    async def reply(self, uuid: str, message: str) -> dict[str, Any]:
        return await self._client._post_raw(
            f"/support/tickets/{uuid}/messages",
            {"message": message},
        )

    async def close_ticket(self, uuid: str) -> None:
        await self._client._post_void(f"/support/tickets/{uuid}/close", {})

    async def rate_ticket(self, uuid: str, rating: int, comment: str | None = None) -> None:
        body: dict[str, Any] = {"rating": rating}
        if comment is not None:
            body["comment"] = comment
        await self._client._post_void(f"/support/tickets/{uuid}/rate", body)
