"""Support tickets.

Tickets are served by the ngris support desk, not the management API: every
call goes to ``support_base_url`` (default ``https://support.ngris.com``)
under ``/api/support/``, with the same API key.
"""

from __future__ import annotations

from typing import Any

from ngris.services._base import AsyncBaseService, BaseService

_TICKETS = "/api/support/tickets"


def _rate_body(rating: int, comment: str | None) -> dict[str, Any]:
    body: dict[str, Any] = {"rating": rating}
    if comment is not None:
        body["comment"] = comment
    return body


class SupportService(BaseService):
    """Sync support service."""

    def _desk(self) -> str:
        return self._client._config.support_base_url

    def list_tickets(self) -> list[dict[str, Any]]:
        resp = self._client._get(_TICKETS, base_url=self._desk())
        tickets: list[dict[str, Any]] = resp.json()
        return tickets

    def create_ticket(self, data: dict[str, Any]) -> dict[str, Any]:
        """Open a ticket. ``data`` takes ``subject``, ``message``, ``category``
        and ``priority``."""
        return self._client._post_raw(_TICKETS, data, base_url=self._desk())

    def get_ticket(self, uuid: str) -> dict[str, Any]:
        """The ticket and its messages: ``{"ticket": ..., "messages": [...]}``."""
        return self._client._get_raw(f"{_TICKETS}/{uuid}", base_url=self._desk())

    def reply(self, uuid: str, message: str) -> dict[str, Any]:
        return self._client._post_raw(f"{_TICKETS}/{uuid}/messages", {"message": message}, base_url=self._desk())

    def close_ticket(self, uuid: str) -> None:
        self._client._post_void(f"{_TICKETS}/{uuid}/close", {}, base_url=self._desk())

    def rate_ticket(self, uuid: str, rating: int, comment: str | None = None) -> None:
        self._client._post_void(f"{_TICKETS}/{uuid}/rate", _rate_body(rating, comment), base_url=self._desk())


class AsyncSupportService(AsyncBaseService):
    """Async support service."""

    def _desk(self) -> str:
        return self._client._config.support_base_url

    async def list_tickets(self) -> list[dict[str, Any]]:
        resp = await self._client._get(_TICKETS, base_url=self._desk())
        tickets: list[dict[str, Any]] = resp.json()
        return tickets

    async def create_ticket(self, data: dict[str, Any]) -> dict[str, Any]:
        return await self._client._post_raw(_TICKETS, data, base_url=self._desk())

    async def get_ticket(self, uuid: str) -> dict[str, Any]:
        return await self._client._get_raw(f"{_TICKETS}/{uuid}", base_url=self._desk())

    async def reply(self, uuid: str, message: str) -> dict[str, Any]:
        return await self._client._post_raw(
            f"{_TICKETS}/{uuid}/messages", {"message": message}, base_url=self._desk()
        )

    async def close_ticket(self, uuid: str) -> None:
        await self._client._post_void(f"{_TICKETS}/{uuid}/close", {}, base_url=self._desk())

    async def rate_ticket(self, uuid: str, rating: int, comment: str | None = None) -> None:
        await self._client._post_void(f"{_TICKETS}/{uuid}/rate", _rate_body(rating, comment), base_url=self._desk())
