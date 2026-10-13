from __future__ import annotations

from datetime import datetime
from typing import Optional

from ngris.models._common import NgrisModel


class DedicatedIPAssignment(NgrisModel):
    uuid: str | None = None
    # Deprecated: the integer ids below are removed from API responses at the
    # integer-id sunset (https://ngris.com/docs/public-ids). Use the *uuid fields.
    id: int | None = None
    user_id: int | None = None
    ip_address: str
    region_slug: str
    status: str
    created_at: datetime


class DedicatedIPRequest(NgrisModel):
    uuid: str | None = None
    assignment_uuid: str | None = None
    # Deprecated: the integer ids below are removed from API responses at the
    # integer-id sunset (https://ngris.com/docs/public-ids). Use the *uuid fields.
    id: int | None = None
    user_id: int | None = None
    region_slug: str
    reason: Optional[str] = None
    status: str
    created_at: datetime


__all__ = ["DedicatedIPAssignment", "DedicatedIPRequest"]
