from __future__ import annotations

from datetime import datetime

from ngris.models._common import NgrisModel


class TrafficPolicy(NgrisModel):
    uuid: str | None = None
    endpoint_uuid: str | None = None
    # Deprecated: the integer ids below are removed from API responses at the
    # integer-id sunset (https://ngris.com/docs/public-ids). Use the *uuid fields.
    id: int | None = None
    endpoint_id: int | None = None
    name: str
    description: str | None = None
    enabled: bool
    priority: int
    created_at: datetime
    updated_at: datetime


class TrafficPolicyRule(NgrisModel):
    uuid: str | None = None
    policy_uuid: str | None = None
    id: int | None = None  # deprecated: use uuid
    policy_id: int | None = None  # deprecated: use policy_uuid
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
