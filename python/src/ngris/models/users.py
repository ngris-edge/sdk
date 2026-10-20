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
    # No user answer sends it any more (payment methods are account-scoped):
    # None. Read the account's verification status instead.
    has_valid_payment_method: bool | None = None
    # kyc_status removed — identity verification is account-scoped (server mig
    # 306); read it from the account verification-status endpoint instead.


class UserProfile(NgrisModel):
    """The caller's own profile, as GET /user and PUT /user answer it.

    Identity only: the plan, limits, balance and verification belong to the
    account (``users.get_plan()``, ``accounts.get()``).
    """

    uuid: str | None = None
    id: int | None = None  # deprecated: use uuid (removed at the integer-id sunset)
    username: str
    full_name: str  # "" when not set
    email: str
    email_verified: bool
    pending_email: str | None = None  # only while an email change awaits confirmation
    role: str = "user"  # the API leaves out the default "user" role
    status: str
    mfa_enabled: bool
    created_at: datetime
    last_login_at: datetime | None = None  # left out before the first sign-in


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


__all__ = ["User", "UserProfile", "UserPlan", "UsageTotals"]
