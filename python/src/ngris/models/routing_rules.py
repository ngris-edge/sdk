from __future__ import annotations

from datetime import datetime

from ngris.models._common import NgrisModel


class RoutingRuleCondition(NgrisModel):
    condition_type: str
    condition_key: str | None = None
    pattern: str
    negate: bool = False


class RoutingRule(NgrisModel):
    uuid: str | None = None
    endpoint_uuid: str | None = None
    # Deprecated: the integer ids below are removed from API responses at the
    # integer-id sunset (https://ngris.com/docs/public-ids). Use the *uuid fields.
    id: int | None = None
    endpoint_id: int | None = None
    name: str
    priority: int
    target_agent_id: str
    target_agent_tags: str | None = None
    enabled: bool
    conditions: list[RoutingRuleCondition] | None = None
    created_at: datetime
    updated_at: datetime


class CreateRoutingRuleRequest(NgrisModel):
    name: str
    priority: int = 0
    target_agent_id: str | None = None
    target_agent_tags: str | None = None
    enabled: bool = True
    conditions: list[RoutingRuleCondition] | None = None


__all__ = ["RoutingRuleCondition", "RoutingRule", "CreateRoutingRuleRequest"]
