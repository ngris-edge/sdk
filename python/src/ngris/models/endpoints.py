from __future__ import annotations

from datetime import datetime

from ngris.models._common import NgrisModel


class Endpoint(NgrisModel):
    uuid: str
    user_uuid: str | None = None
    account_uuid: str | None = None
    domain_uuid: str | None = None
    application_uuid: str | None = None
    certificate_uuid: str | None = None
    # Deprecated: the integer ids below are removed from API responses at the
    # integer-id sunset (https://ngris.com/docs/public-ids). Use the *uuid fields.
    id: int | None = None
    user_id: int | None = None
    domain_id: int | None = None
    certificate_id: int | None = None
    subdomain: str
    protocol: str
    # Endpoints are region-less now — region is a property of the serving tunnel,
    # not the endpoint, and the server no longer emits it. Kept optional for
    # backward compat with older API responses; defaults to None.
    region: str | None = None
    is_custom: bool
    status: str
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
    domain_uuid: str | None = None
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


class HealthCheck(NgrisModel):
    """One health probe of an endpoint (``GET /endpoints/{uuid}/health``)."""

    # "healthy" when the probe passed; any other value is a failed probe.
    status: str
    # HTTP status the probe got, when it got one.
    status_code: int | None = None
    latency_ms: int | None = None
    error_message: str | None = None
    # The zero time (0001-01-01) when the latest probe came from the status
    # cache without a timestamp.
    checked_at: datetime
    # Internal row id of the probe; 0 when the latest probe came from the
    # status cache. There is no uuid for probes.
    id: int | None = None


class HealthStatus(NgrisModel):
    """An endpoint's health: active agent, uptime and the probes behind it.

    Requires the plan's endpoint-health feature (403 otherwise).
    """

    endpoint_uuid: str | None = None
    # Deprecated: removed from API responses at the integer-id sunset
    # (https://ngris.com/docs/public-ids). Use ``endpoint_uuid``.
    endpoint_id: int | None = None
    # True while at least one agent serves the endpoint.
    has_active_agent: bool
    # Share of healthy probes, in percent (0-100), over each window. 0 when
    # the window has no probes.
    uptime_24h: float
    uptime_7d: float
    uptime_30d: float
    # Average probe latency over the last 24 hours, in milliseconds.
    avg_latency_ms: float
    # The latest probe, or None before the first one.
    last_check: HealthCheck | None = None
    # Up to the 50 latest probes, newest first.
    recent_checks: list[HealthCheck] = []


__all__ = ["Endpoint", "CreateEndpointRequest", "EndpointAuthSettings", "HealthCheck", "HealthStatus"]
