from __future__ import annotations

from datetime import datetime

from ngris.models._common import NgrisModel


class User(NgrisModel):
    id: int
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
    organization_id: int | None = None
    allow_organizations: bool = False
    allowed_protocols: str | None = None
    allowed_regions: str | None = None
    has_valid_payment_method: bool = False
    # kyc_status removed — identity verification is account-scoped (server mig
    # 306); read it from the account verification-status endpoint instead.


class UserPlan(NgrisModel):
    id: int | None = None
    name: str | None = None
    default_domain_id: int | None = None
    default_domain_name: str | None = None


class UsageTotals(NgrisModel):
    requests_total: int
    bytes_in_total: int
    bytes_out_total: int


__all__ = ["User", "UserPlan", "UsageTotals"]
