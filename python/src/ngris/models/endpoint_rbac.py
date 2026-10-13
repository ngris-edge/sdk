from __future__ import annotations

from datetime import datetime

from ngris.models._common import NgrisModel


class EndpointClient(NgrisModel):
    uuid: str | None = None
    endpoint_uuid: str | None = None
    # Deprecated: the integer ids below are removed from API responses at the
    # integer-id sunset (https://ngris.com/docs/public-ids). Use the *uuid fields.
    id: int | None = None
    endpoint_id: int | None = None
    identifier: str
    display_name: str
    email: str | None = None
    status: str
    username: str | None = None
    registration_source: str | None = None
    last_seen_at: datetime | None = None


class EndpointRole(NgrisModel):
    uuid: str | None = None
    endpoint_uuid: str | None = None
    # Deprecated: the integer ids below are removed from API responses at the
    # integer-id sunset (https://ngris.com/docs/public-ids). Use the *uuid fields.
    id: int | None = None
    endpoint_id: int | None = None
    name: str
    description: str | None = None
    priority: int
    is_default: bool
    permissions: dict | None = None


class EndpointRoleMembership(NgrisModel):
    client_uuid: str | None = None
    role_uuid: str | None = None
    assigned_by_uuid: str | None = None
    # Deprecated: the integer ids below are removed from API responses at the
    # integer-id sunset (https://ngris.com/docs/public-ids). Use the *uuid fields.
    id: int | None = None
    endpoint_id: int | None = None
    client_id: int | None = None
    role_id: int | None = None


class EndpointClientSession(NgrisModel):
    uuid: str | None = None
    endpoint_uuid: str | None = None
    client_uuid: str | None = None
    # Deprecated: the integer ids below are removed from API responses at the
    # integer-id sunset (https://ngris.com/docs/public-ids). Use the *uuid fields.
    id: int | None = None
    endpoint_id: int | None = None
    client_id: int | None = None
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
