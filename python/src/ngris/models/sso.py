from __future__ import annotations

from typing import Optional

from ngris.models._common import NgrisModel


class SSOConfig(NgrisModel):
    id: int
    organization_id: int
    email_domain: str
    provider_type: str
    client_id: str
    auth_url: Optional[str] = None
    token_url: Optional[str] = None
    userinfo_url: Optional[str] = None
    scopes: Optional[str] = None
    status: str


__all__ = ["SSOConfig"]
