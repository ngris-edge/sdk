from __future__ import annotations

from datetime import datetime
from typing import Optional

from ngris.models._common import NgrisModel


class TunnelAgent(NgrisModel):
    # A tunnel agent is addressed by its own ``agent_id`` string.
    tunnel_uuid: Optional[str] = None
    id: Optional[int] = None  # deprecated (list-only row id)
    tunnel_id: Optional[int] = None  # deprecated: use tunnel_uuid
    agent_id: str
    agent_name: Optional[str] = None
    agent_tags: Optional[str] = None
    agent_version: str
    ip: str
    port: int
    weight: int
    status: str
    connected_at: datetime
    last_seen_at: datetime


class Tunnel(NgrisModel):
    uuid: Optional[str] = None
    user_uuid: Optional[str] = None
    account_uuid: Optional[str] = None
    endpoint_uuid: Optional[str] = None
    # Deprecated: the integer ids below are removed from API responses at the
    # integer-id sunset (https://ngris.com/docs/public-ids). Use the *uuid fields.
    id: Optional[int] = None
    user_id: Optional[int] = None
    endpoint_id: Optional[int] = None
    name: str
    type: str
    local_address: str
    public_url: Optional[str] = None
    status: str
    agent_count: int
    created_at: datetime
    updated_at: datetime


__all__ = ["Tunnel", "TunnelAgent"]
