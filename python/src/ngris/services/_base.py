from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ngris._base_client import AsyncBaseClient, SyncBaseClient


class BaseService:
    """Base class for sync service modules."""

    def __init__(self, client: SyncBaseClient) -> None:
        self._client = client


class AsyncBaseService:
    """Base class for async service modules."""

    def __init__(self, client: AsyncBaseClient) -> None:
        self._client = client
