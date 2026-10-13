from __future__ import annotations

from datetime import datetime
from typing import Optional

from ngris.models._common import NgrisModel


class ClientCA(NgrisModel):
    uuid: str | None = None
    user_uuid: str | None = None
    # Deprecated: the integer ids below are removed from API responses at the
    # integer-id sunset (https://ngris.com/docs/public-ids). Use the *uuid fields.
    id: int | None = None
    user_id: int | None = None
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
    ca_uuids: Optional[list[str]] = None
    endpoint_uuid: Optional[str] = None
    ca_ids: Optional[list[int]] = None  # deprecated: use ca_uuids


__all__ = ["ClientCA", "CreateClientCARequest", "MTLSConfig"]
