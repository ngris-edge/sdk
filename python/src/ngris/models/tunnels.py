from __future__ import annotations

from datetime import datetime
from typing import Optional

from ngris.models._common import NgrisModel


class TunnelAgent(NgrisModel):
    id: int
    tunnel_id: int
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
    id: int
    user_id: int
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
