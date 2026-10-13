from __future__ import annotations

from datetime import datetime
from typing import Optional

from ngris.models._common import NgrisModel


class TrafficLog(NgrisModel):
    uuid: Optional[str] = None
    endpoint_uuid: Optional[str] = None
    tunnel_uuid: Optional[str] = None
    # Deprecated: the integer ids below are removed from API responses at the
    # integer-id sunset (https://ngris.com/docs/public-ids). Use the *uuid fields.
    id: Optional[int] = None
    endpoint_id: Optional[int] = None
    tunnel_id: Optional[int] = None
    source_ip: Optional[str] = None
    method: Optional[str] = None
    path: Optional[str] = None
    request_url: Optional[str] = None
    status_code: Optional[int] = None
    latency_ms: Optional[float] = None
    bytes_in: Optional[int] = None
    bytes_out: Optional[int] = None
    firewall_action: Optional[str] = None
    rate_limit_action: Optional[str] = None
    created_at: Optional[datetime] = None


class TrafficMetrics(NgrisModel):
    total_requests: int
    total_bytes_in: int
    total_bytes_out: int
    avg_latency_ms: Optional[float] = None
    error_rate: Optional[float] = None


__all__ = ["TrafficLog", "TrafficMetrics"]
