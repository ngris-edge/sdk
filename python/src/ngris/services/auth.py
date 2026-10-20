from __future__ import annotations

from ngris.models.auth import LoginResponse, TokenResponse
from ngris.services._base import AsyncBaseService, BaseService


def _mfa_body(
    username: str | None,
    password: str | None,
    token: str | None,
    mfa_challenge_token: str | None,
) -> dict[str, str]:
    # /auth/mfa takes {mfa_challenge_token, token} (preferred: the token
    # /auth/login answered with mfa_required) or the legacy
    # {username, password, token}.
    if token is None:
        raise TypeError("mfa_verify() needs token= (the authenticator or backup code)")
    if mfa_challenge_token is not None:
        if username is not None or password is not None:
            raise TypeError("mfa_verify() takes mfa_challenge_token= or username + password, not both")
        return {"mfa_challenge_token": mfa_challenge_token, "token": token}
    if username is None or password is None:
        raise TypeError("mfa_verify() needs mfa_challenge_token= (from login()) or username + password")
    return {"username": username, "password": password, "token": token}


class AuthService(BaseService):
    """Sync authentication service."""

    def login(self, username: str, password: str) -> LoginResponse:
        """Log in with username + password.

        If the response indicates ``mfa_required``, it carries no token but an
        ``mfa_challenge_token``: follow up with
        ``mfa_verify(mfa_challenge_token=resp.mfa_challenge_token, token=code)``
        (a separate endpoint) — there is no inline MFA field on /auth/login.
        """
        return self._client._post_json(
            "/auth/login",
            {"username": username, "password": password},
            LoginResponse,
        )

    def mfa_verify(
        self,
        username: str | None = None,
        password: str | None = None,
        token: str | None = None,
        *,
        mfa_challenge_token: str | None = None,
    ) -> LoginResponse:
        """Second step of an MFA login: the code (``token``) plus either the
        ``mfa_challenge_token`` :meth:`login` answered (preferred) or, the
        legacy form, the username + password again.

        The answer's ``token`` is the session token.
        """
        return self._client._post_json(
            "/auth/mfa",
            _mfa_body(username, password, token, mfa_challenge_token),
            LoginResponse,
        )

    def forgot_password(self, email: str) -> None:
        self._client._post_void("/auth/forgot-password", {"email": email})

    def reset_password(self, token: str, new_password: str) -> None:
        self._client._post_void(
            "/auth/reset-password",
            {"token": token, "new_password": new_password},
        )

    def generate_token(self) -> TokenResponse:
        """Mint a fresh API key for the authenticated user.

        The server hardcodes the description ("Regenerated via /auth/token")
        and ignores any client-supplied fields, so this method takes no args.
        Use :meth:`Ngris.api_keys.create_api_key` for a custom description.
        """
        return self._client._post_json("/auth/token", {}, TokenResponse)

    def verify_email(self, token: str) -> None:
        self._client._get_void("/auth/verify-email", params={"token": token})

    def resend_verification(self) -> None:
        self._client._post_void("/auth/resend-verification", {})


class AsyncAuthService(AsyncBaseService):
    """Async authentication service."""

    async def login(self, username: str, password: str) -> LoginResponse:
        return await self._client._post_json(
            "/auth/login",
            {"username": username, "password": password},
            LoginResponse,
        )

    async def mfa_verify(
        self,
        username: str | None = None,
        password: str | None = None,
        token: str | None = None,
        *,
        mfa_challenge_token: str | None = None,
    ) -> LoginResponse:
        return await self._client._post_json(
            "/auth/mfa",
            _mfa_body(username, password, token, mfa_challenge_token),
            LoginResponse,
        )

    async def forgot_password(self, email: str) -> None:
        await self._client._post_void("/auth/forgot-password", {"email": email})

    async def reset_password(self, token: str, new_password: str) -> None:
        await self._client._post_void(
            "/auth/reset-password",
            {"token": token, "new_password": new_password},
        )

    async def generate_token(self) -> TokenResponse:
        return await self._client._post_json("/auth/token", {}, TokenResponse)

    async def verify_email(self, token: str) -> None:
        await self._client._get_void("/auth/verify-email", params={"token": token})

    async def resend_verification(self) -> None:
        await self._client._post_void("/auth/resend-verification", {})
