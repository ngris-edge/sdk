from __future__ import annotations

from typing import Optional

from ngris.models._common import NgrisModel


class SSOConfig(NgrisModel):
    uuid: Optional[str] = None
    account_uuid: Optional[str] = None
    # Deprecated: the integer ids below are removed from API responses at the
    # integer-id sunset (https://ngris.com/docs/public-ids). Use the *uuid fields.
    id: Optional[int] = None
    account_id: Optional[int] = None
    organization_id: Optional[int] = None  # legacy (pre-accounts); unused
    email_domain: str
    provider_type: str
    client_id: str
    auth_url: Optional[str] = None
    token_url: Optional[str] = None
    userinfo_url: Optional[str] = None
    scopes: Optional[str] = None
    status: str


__all__ = ["SSOConfig"]
