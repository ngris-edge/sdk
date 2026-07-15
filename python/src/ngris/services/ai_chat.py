from __future__ import annotations

from typing import Any

from ngris.services._base import AsyncBaseService, BaseService


class AIChatService(BaseService):
    """Sync AI chat service."""

    def list_sessions(self) -> list[dict[str, Any]]:
        resp = self._client._get("/ai/sessions")
        return resp.json()

    def create_session(self, title: str | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if title is not None:
            body["title"] = title
        return self._client._post_raw("/ai/sessions", body)

    def get_session(self, session_id: str) -> dict[str, Any]:
        return self._client._get_raw(f"/ai/sessions/{session_id}")

    def delete_session(self, session_id: str) -> None:
        self._client._delete_void(f"/ai/sessions/{session_id}")

    def chat(self, session_id: str, message: str) -> dict[str, Any]:
        return self._client._post_raw(
            f"/ai/sessions/{session_id}/chat", {"message": message}
        )


class AsyncAIChatService(AsyncBaseService):
    """Async AI chat service."""

    async def list_sessions(self) -> list[dict[str, Any]]:
        resp = await self._client._get("/ai/sessions")
        return resp.json()

    async def create_session(self, title: str | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if title is not None:
            body["title"] = title
        return await self._client._post_raw("/ai/sessions", body)

    async def get_session(self, session_id: str) -> dict[str, Any]:
        return await self._client._get_raw(f"/ai/sessions/{session_id}")

    async def delete_session(self, session_id: str) -> None:
        await self._client._delete_void(f"/ai/sessions/{session_id}")

    async def chat(self, session_id: str, message: str) -> dict[str, Any]:
        return await self._client._post_raw(
            f"/ai/sessions/{session_id}/chat", {"message": message}
        )
