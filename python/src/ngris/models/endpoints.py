from __future__ import annotations

from datetime import datetime

from ngris.models._common import NgrisModel


class Endpoint(NgrisModel):
    id: int
    uuid: str
    user_id: int
    domain_id: int | None = None
    subdomain: str
    protocol: str
    # Endpoints are region-less now — region is a property of the serving tunnel,
    # not the endpoint, and the server no longer emits it. Kept optional for
    # backward compat with older API responses; defaults to None.
    region: str | None = None
    is_custom: bool
    status: str
    certificate_id: int | None = None
    dedicated_tcp_port: int | None = None
    dedicated_udp_port: int | None = None
    mtls_mode: str
    ephemeral: bool = False
    # Public FQDN of the endpoint, e.g. "my-api.ngris.app" (subdomain + domain),
    # computed server-side. Mirrors Go models.Endpoint.Hostname ("hostname").
    hostname: str | None = None
    # NOTE: public_url is the BARE FQDN with NO scheme (it was previously
    # "https://..."). One endpoint serves http/tcp/udp, so prepend the scheme
    # yourself (https:// for http/unified endpoints). Currently equals `hostname`;
    # prefer `hostname` for new code.
    public_url: str | None = None
    created_at: datetime
    updated_at: datetime
    last_active_at: datetime | None = None


class CreateEndpointRequest(NgrisModel):
    subdomain: str | None = None
    is_custom: bool | None = None
    domain_id: int | None = None
    # Endpoints are protocol-agnostic (always "unified") — the server no longer
    # accepts a protocol on create. Protocol is chosen per-tunnel by the agent.
    # Field kept optional for backward compat; it is ignored server-side.
    protocol: str | None = None
    # Endpoints are region-less — region is a property of the serving tunnel
    # (GeoDNS steers traffic), so the server no longer requires or stores it.
    # Field kept optional for backward compat; it is ignored server-side.
    region: str | None = None


class EndpointAuthSettings(NgrisModel):
    mode: str
    enforce_https: bool = False
    config: dict | None = None


class HealthStatus(NgrisModel):
    status: str
    uptime_seconds: int | None = None
    last_check: datetime | None = None


__all__ = ["Endpoint", "CreateEndpointRequest", "EndpointAuthSettings", "HealthStatus"]
