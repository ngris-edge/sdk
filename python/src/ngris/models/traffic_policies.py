from __future__ import annotations

from datetime import datetime

from ngris.models._common import NgrisModel


class TrafficPolicy(NgrisModel):
    id: int
    endpoint_id: int
    name: str
    description: str | None = None
    enabled: bool
    priority: int
    created_at: datetime
    updated_at: datetime


class TrafficPolicyRule(NgrisModel):
    id: int | None = None
    policy_id: int | None = None
    phase: str
    rule_type: str
    name: str | None = None
    priority: int = 0
    enabled: bool = True
    config: dict | None = None


class CreateTrafficPolicyRequest(NgrisModel):
    name: str
    description: str | None = None
    enabled: bool = True
    priority: int = 100


__all__ = ["TrafficPolicy", "TrafficPolicyRule", "CreateTrafficPolicyRequest"]
