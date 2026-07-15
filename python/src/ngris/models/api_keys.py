from __future__ import annotations

from datetime import datetime
from typing import Optional

from ngris.models._common import NgrisModel


class APIKey(NgrisModel):
    id: int
    user_id: int
    key: str
    description: str
    created_at: datetime
    last_used_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    allowed_ips: Optional[str] = None


class AuthToken(NgrisModel):
    id: int
    user_id: int
    token: str
    description: str
    endpoint_id: Optional[int] = None
    tunnel_id: Optional[int] = None
    status: str
    created_at: datetime
    last_used_at: Optional[datetime] = None


__all__ = ["APIKey", "AuthToken"]
