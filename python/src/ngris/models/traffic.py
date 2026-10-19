from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

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
    # The edge's X-Request-Id for this request: the value the client got in
    # the X-Request-Id response header. None on TCP/UDP sessions, entries from
    # before request ids were recorded and some edge-generated error responses.
    # Find one request's entry with traffic.list_logs(request_id=...).
    request_id: Optional[str] = None
    source_ip: Optional[str] = None
    method: Optional[str] = None
    path: Optional[str] = None
    # host is None on TCP/UDP sessions. tunnel_type is "http", "tcp" or "udp";
    # public_url is the endpoint's address ("tcp://host:port" for TCP/UDP).
    host: Optional[str] = None
    request_url: Optional[str] = None
    tunnel_type: Optional[str] = None
    public_url: Optional[str] = None
    # The serving edge region, and the HTTP version ("HTTP/1.1", "HTTP/2",
    # "HTTP/3"; None on TCP/UDP sessions).
    region: Optional[str] = None
    http_version: Optional[str] = None
    # The session id of a TCP/UDP session row (None on HTTP rows).
    connection_id: Optional[str] = None
    # status_code is what the client got; origin_status what the origin
    # answered (None when the edge answered by itself).
    status_code: Optional[int] = None
    origin_status: Optional[int] = None
    # Timing in ms. duration_ms is the whole request and equals
    # edge_ms + origin_ttfb_ms + transfer_ms; latency_ms is the origin's time
    # to first byte (= origin_ttfb_ms). A phase that didn't happen is None.
    latency_ms: Optional[float] = None
    duration_ms: Optional[int] = None
    edge_ms: Optional[int] = None
    origin_ttfb_ms: Optional[int] = None
    transfer_ms: Optional[int] = None
    bytes_in: Optional[int] = None
    bytes_out: Optional[int] = None
    firewall_action: Optional[str] = None
    rate_limit_action: Optional[str] = None
    is_replay: Optional[bool] = None
    # The client's geo / network lookup (country, asn, …).
    geo_info: Optional[dict[str, Any]] = None
    # IP reputation of source_ip: a spam score (0-100) and a health label.
    spam_score: Optional[int] = None
    ip_health: Optional[str] = None
    # The owning account's uuid: on responses to admin callers only.
    account_uuid: Optional[str] = None
    created_at: Optional[datetime] = None


class TrafficMetrics(NgrisModel):
    total_requests: int
    total_bytes_in: int
    total_bytes_out: int
    avg_latency_ms: Optional[float] = None
    error_rate: Optional[float] = None


__all__ = ["TrafficLog", "TrafficMetrics"]
