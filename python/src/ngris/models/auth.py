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
    id: int
    token: str
    description: str | None = None


__all__ = ["LoginRequest", "MFAVerifyRequest", "LoginResponse", "TokenResponse"]
