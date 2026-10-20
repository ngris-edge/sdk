from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import AliasChoices, Field, ValidationError, field_validator

from ngris.models._common import NgrisModel
from ngris.models.users import User


class LoginRequest(NgrisModel):
    username: str
    password: str


class MFAVerifyRequest(NgrisModel):
    # The /auth/mfa body: the mfa_challenge_token /auth/login answered plus the
    # code (preferred), or the legacy username + password + code.
    mfa_challenge_token: str | None = None
    username: str | None = None
    password: str | None = None
    token: str


class LoginUser(NgrisModel):
    """The signed-in user of the sign-in answers that don't carry the whole
    user: /auth/login when MFA is required, and /auth/mfa."""

    uuid: str | None = None
    id: int | None = None  # deprecated: use uuid (removed at the integer-id sunset)
    username: str
    email: str
    role: str


class LoginResponse(NgrisModel):
    """The answer of /auth/login and /auth/mfa.

    A sign-in that needs MFA answers ``mfa_required=True``, no token, an
    ``mfa_challenge_token`` (valid ``mfa_expires_in`` seconds) and a
    :class:`LoginUser`; pass the challenge token and the code to
    ``auth.mfa_verify``. Otherwise ``token`` is the session token (/auth/mfa
    sends it as ``access_token``), and ``user`` is the full :class:`User` after
    /auth/login, a :class:`LoginUser` after /auth/mfa.
    """

    token: str | None = Field(default=None, validation_alias=AliasChoices("token", "access_token"))
    user: User | LoginUser | None = None
    mfa_required: bool = False
    mfa_challenge_token: str | None = None
    mfa_expires_in: int | None = None

    @field_validator("user", mode="before")
    @classmethod
    def _full_or_short_user(cls, value: Any) -> Any:
        # The full User when the answer carries one, else the short LoginUser
        # (an MFA answer). Decided here: a plain union could pick LoginUser for
        # a full user too, since every LoginUser field is there.
        if isinstance(value, dict):
            try:
                return User.model_validate(value)
            except ValidationError:
                return LoginUser.model_validate(value)
        return value


class TokenResponse(NgrisModel):
    # POST /auth/token answers {"token": ...} only; uuid / id are kept optional
    # for older servers that also returned the key's id.
    uuid: str | None = None
    id: int | None = None  # deprecated (integer ids, see https://ngris.com/docs/public-ids)
    token: str
    description: str | None = None


__all__ = ["LoginRequest", "MFAVerifyRequest", "LoginUser", "LoginResponse", "TokenResponse"]
