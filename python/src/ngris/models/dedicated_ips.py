from __future__ import annotations

from datetime import datetime
from typing import Optional

from ngris.models._common import NgrisModel


class DedicatedIPAssignment(NgrisModel):
    id: int
    user_id: int
    ip_address: str
    region_slug: str
    status: str
    created_at: datetime


class DedicatedIPRequest(NgrisModel):
    id: int
    user_id: int
    region_slug: str
    reason: Optional[str] = None
    status: str
    created_at: datetime


__all__ = ["DedicatedIPAssignment", "DedicatedIPRequest"]
