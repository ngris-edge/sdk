from __future__ import annotations

from ngris.models.auth import LoginResponse, TokenResponse
from ngris.services._base import AsyncBaseService, BaseService


class AuthService(BaseService):
    """Sync authentication service."""

    def login(self, username: str, password: str) -> LoginResponse:
        """Log in with username + password.

        If the response indicates ``mfa_required``, follow up with
        :meth:`mfa_verify` (a separate endpoint) — there is no inline
        MFA field on /auth/login.
        """
        return self._client._post_json(
            "/auth/login",
            {"username": username, "password": password},
            LoginResponse,
        )

    def mfa_verify(self, username: str, password: str, token: str) -> LoginResponse:
        """Second step of MFA login: re-send credentials plus the TOTP token."""
        return self._client._post_json(
            "/auth/mfa",
            {"username": username, "password": password, "token": token},
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

    async def mfa_verify(self, username: str, password: str, token: str) -> LoginResponse:
        return await self._client._post_json(
            "/auth/mfa",
            {"username": username, "password": password, "token": token},
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
