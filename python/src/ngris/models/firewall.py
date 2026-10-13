from __future__ import annotations

from datetime import datetime
from typing import Optional

from ngris.models._common import NgrisModel


class FirewallCondition(NgrisModel):
    # Firewall ids were always uuid strings; ``uuid`` / ``policy_uuid`` carry
    # the same values under the public-id names.
    id: str
    uuid: Optional[str] = None
    policy_id: str
    policy_uuid: Optional[str] = None
    condition_type: str
    operator: str
    condition_value: str
    logical_operator: Optional[str] = None


class FirewallPolicy(NgrisModel):
    id: str
    uuid: Optional[str] = None
    user_uuid: Optional[str] = None
    account_uuid: Optional[str] = None
    user_id: Optional[int] = None  # deprecated: use user_uuid
    name: str
    description: Optional[str] = None
    priority: int
    action: str
    enabled: bool
    conditions: Optional[list[FirewallCondition]] = None
    created_at: datetime
    updated_at: datetime


class RateLimitRule(NgrisModel):
    uuid: Optional[str] = None
    endpoint_uuid: Optional[str] = None
    user_uuid: Optional[str] = None
    account_uuid: Optional[str] = None
    # Deprecated: the integer ids below are removed from API responses at the
    # integer-id sunset (https://ngris.com/docs/public-ids). Use the *uuid fields.
    id: Optional[int] = None
    endpoint_id: Optional[int] = None
    user_id: Optional[int] = None
    name: str
    source_ip: Optional[str] = None
    requests_per_window: int
    window_size_seconds: int
    action: str
    status: str
    priority: int
    description: Optional[str] = None


__all__ = ["FirewallCondition", "FirewallPolicy", "RateLimitRule"]
