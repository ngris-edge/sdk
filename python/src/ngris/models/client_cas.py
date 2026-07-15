from __future__ import annotations

from datetime import datetime
from typing import Optional

from ngris.models._common import NgrisModel


class ClientCA(NgrisModel):
    id: int
    user_id: int
    name: str
    description: Optional[str] = None
    fingerprint: Optional[str] = None
    subject_cn: Optional[str] = None
    issuer_cn: Optional[str] = None
    not_before: Optional[datetime] = None
    not_after: Optional[datetime] = None


class CreateClientCARequest(NgrisModel):
    name: str
    certificate: str = ""


class MTLSConfig(NgrisModel):
    mode: str
    ca_ids: Optional[list[int]] = None


__all__ = ["ClientCA", "CreateClientCARequest", "MTLSConfig"]
