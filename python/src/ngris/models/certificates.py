from __future__ import annotations

from datetime import datetime
from typing import Optional

from ngris.models._common import NgrisModel


class Certificate(NgrisModel):
    uuid: str
    domain_uuid: Optional[str] = None
    owner_user_uuid: Optional[str] = None
    account_uuid: Optional[str] = None
    # Deprecated: the integer ids below are removed from API responses at the
    # integer-id sunset (https://ngris.com/docs/public-ids). Use the *uuid fields.
    id: Optional[int] = None
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
    domain_uuid: Optional[str] = None
    certificate: str = ""
    private_key: str = ""
    chain: Optional[str] = None


__all__ = ["Certificate", "UploadCertificateRequest"]
