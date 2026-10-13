from __future__ import annotations

from datetime import datetime
from typing import Optional

from ngris.models._common import NgrisModel


class Domain(NgrisModel):
    uuid: str
    account_uuid: Optional[str] = None
    created_by_uuid: Optional[str] = None
    # Deprecated: the integer ids below are removed from API responses at the
    # integer-id sunset (https://ngris.com/docs/public-ids). Use the *uuid fields.
    id: Optional[int] = None
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
    # The DNS provider's own record id (not an ngris id; unaffected by the
    # move to public uuids).
    id: int | str | None = None
    domain_id: Optional[int] = None  # deprecated
    domain_uuid: Optional[str] = None
    record_type: str
    name: str
    value: str
    ttl: int
    priority: Optional[int] = None


class CreateDomainRequest(NgrisModel):
    name: str
    provider: Optional[str] = None


__all__ = ["Domain", "DNSRecord", "CreateDomainRequest"]
