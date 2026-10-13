from __future__ import annotations

from datetime import datetime
from typing import Optional

from ngris.models._common import NgrisModel


class APIKey(NgrisModel):
    uuid: str | None = None
    user_uuid: str | None = None
    account_uuid: str | None = None
    # Deprecated: the integer ids below are removed from API responses at the
    # integer-id sunset (https://ngris.com/docs/public-ids). Use the *uuid fields.
    id: int | None = None
    user_id: int | None = None
    account_id: int | None = None
    key: str
    description: str
    created_at: datetime
    last_used_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    allowed_ips: Optional[str] = None


class AuthToken(NgrisModel):
    uuid: str | None = None
    user_uuid: str | None = None
    account_uuid: str | None = None
    endpoint_uuid: str | None = None
    tunnel_uuid: str | None = None
    # Deprecated: the integer ids below are removed from API responses at the
    # integer-id sunset (https://ngris.com/docs/public-ids). Use the *uuid fields.
    id: int | None = None
    user_id: int | None = None
    account_id: int | None = None
    endpoint_id: Optional[int] = None
    tunnel_id: Optional[int] = None
    token: str
    description: str
    status: str
    created_at: datetime
    last_used_at: Optional[datetime] = None


__all__ = ["APIKey", "AuthToken"]
