from __future__ import annotations

from datetime import datetime

from ngris.models._common import NgrisModel


class User(NgrisModel):
    uuid: str | None = None
    id: int | None = None  # deprecated: use uuid (removed at the integer-id sunset)
    username: str
    email: str
    role: str
    plan: str
    status: str
    max_tunnels: int
    max_endpoints: int
    max_connections: int
    bandwidth_limit: int
    mfa_enabled: bool
    balance_cents: int
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime | None = None
    allowed_protocols: str | None = None
    allowed_regions: str | None = None
    has_valid_payment_method: bool = False
    # kyc_status removed — identity verification is account-scoped (server mig
    # 306); read it from the account verification-status endpoint instead.


class UserPlan(NgrisModel):
    slug: str | None = None
    name: str | None = None
    default_domain_uuid: str | None = None
    default_domain_name: str | None = None
    id: int | None = None  # deprecated: plans are addressed by slug
    default_domain_id: int | None = None  # deprecated: use default_domain_uuid


class UsageTotals(NgrisModel):
    requests_total: int
    bytes_in_total: int
    bytes_out_total: int


__all__ = ["User", "UserPlan", "UsageTotals"]
