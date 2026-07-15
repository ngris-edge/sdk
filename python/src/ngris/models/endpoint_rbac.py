from __future__ import annotations

from datetime import datetime

from ngris.models._common import NgrisModel


class EndpointClient(NgrisModel):
    id: int
    endpoint_id: int
    identifier: str
    display_name: str
    email: str | None = None
    status: str
    username: str | None = None
    registration_source: str | None = None
    last_seen_at: datetime | None = None


class EndpointRole(NgrisModel):
    id: int
    endpoint_id: int
    name: str
    description: str | None = None
    priority: int
    is_default: bool
    permissions: dict | None = None


class EndpointRoleMembership(NgrisModel):
    id: int
    endpoint_id: int
    client_id: int
    role_id: int


class EndpointClientSession(NgrisModel):
    id: int
    endpoint_id: int
    client_id: int
    ip_address: str | None = None
    user_agent: str | None = None
    expires_at: datetime | None = None
    is_active: bool


__all__ = [
    "EndpointClient",
    "EndpointRole",
    "EndpointRoleMembership",
    "EndpointClientSession",
]
