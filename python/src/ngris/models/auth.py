from __future__ import annotations

from datetime import datetime

from ngris.models._common import NgrisModel
from ngris.models.users import User


class LoginRequest(NgrisModel):
    username: str
    password: str


class MFAVerifyRequest(NgrisModel):
    username: str
    password: str
    token: str


class LoginResponse(NgrisModel):
    token: str | None = None
    user: User | None = None
    mfa_required: bool = False


class TokenResponse(NgrisModel):
    # POST /auth/token answers {"token": ...} only; uuid / id are kept optional
    # for older servers that also returned the key's id.
    uuid: str | None = None
    id: int | None = None  # deprecated (integer ids, see https://ngris.com/docs/public-ids)
    token: str
    description: str | None = None


__all__ = ["LoginRequest", "MFAVerifyRequest", "LoginResponse", "TokenResponse"]
