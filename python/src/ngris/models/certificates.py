from __future__ import annotations

from datetime import datetime
from typing import Optional

from ngris.models._common import NgrisModel


class Certificate(NgrisModel):
    id: int
    uuid: str
    domain_id: Optional[int] = None
    owner_user_id: Optional[int] = None
    name: str
    not_before: Optional[datetime] = None
    not_after: Optional[datetime] = None
    is_active: bool
    is_default: bool
    acme_issued: bool
    created_at: datetime
    updated_at: datetime


class UploadCertificateRequest(NgrisModel):
    name: str
    domain_id: Optional[int] = None
    certificate: str = ""
    private_key: str = ""
    chain: Optional[str] = None


__all__ = ["Certificate", "UploadCertificateRequest"]
