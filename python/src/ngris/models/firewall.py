from __future__ import annotations

from datetime import datetime
from typing import Optional

from ngris.models._common import NgrisModel


class FirewallCondition(NgrisModel):
    id: str
    policy_id: str
    condition_type: str
    operator: str
    condition_value: str
    logical_operator: Optional[str] = None


class FirewallPolicy(NgrisModel):
    id: str
    user_id: int
    name: str
    description: Optional[str] = None
    priority: int
    action: str
    enabled: bool
    conditions: Optional[list[FirewallCondition]] = None
    created_at: datetime
    updated_at: datetime


class RateLimitRule(NgrisModel):
    id: int
    endpoint_id: int
    user_id: int
    name: str
    source_ip: Optional[str] = None
    requests_per_window: int
    window_size_seconds: int
    action: str
    status: str
    priority: int
    description: Optional[str] = None


__all__ = ["FirewallCondition", "FirewallPolicy", "RateLimitRule"]
