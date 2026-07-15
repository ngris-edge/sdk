from __future__ import annotations

from datetime import datetime
from typing import Optional

from ngris.models._common import NgrisModel


class Domain(NgrisModel):
    id: int
    uuid: str
    owner_user_id: Optional[int] = None
    name: str
    plan_access: str
    provider: Optional[str] = None
    provider_config: Optional[str] = None
    is_active: bool
    status: str
    created_at: datetime
    updated_at: datetime


class DNSRecord(NgrisModel):
    id: int
    domain_id: int
    record_type: str
    name: str
    value: str
    ttl: int
    priority: Optional[int] = None


class CreateDomainRequest(NgrisModel):
    name: str
    provider: Optional[str] = None


__all__ = ["Domain", "DNSRecord", "CreateDomainRequest"]
