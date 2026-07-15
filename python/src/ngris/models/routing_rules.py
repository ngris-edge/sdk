from __future__ import annotations

from datetime import datetime

from ngris.models._common import NgrisModel


class RoutingRuleCondition(NgrisModel):
    condition_type: str
    condition_key: str | None = None
    pattern: str
    negate: bool = False


class RoutingRule(NgrisModel):
    id: int
    endpoint_id: int
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
