from __future__ import annotations

from datetime import datetime
from typing import Optional

from ngris.models._common import NgrisModel


class Organization(NgrisModel):
    id: int
    name: str
    slug: str
    plan: Optional[str] = None
    status: str
    description: Optional[str] = None
    website: Optional[str] = None
    owner_id: int
    members_count: int
    max_members: int
    sso_enabled: bool
    two_factor_required: bool
    created_at: datetime
    updated_at: datetime


class OrganizationMember(NgrisModel):
    id: int
    organization_id: int
    user_id: int
    role: str
    status: str
    joined_at: datetime


class OrganizationInvitation(NgrisModel):
    id: int
    organization_id: int
    invited_email: str
    role: str
    status: str
    invited_at: datetime
    expires_at: datetime


__all__ = ["Organization", "OrganizationMember", "OrganizationInvitation"]
