"""Accounts, the API's name for organizations.

An API key belongs to one account, and every request made with it runs in
that account. So the methods below that act on "the account" act on the
key's own account: the API has no route that reads or changes an account by
id, and an API key cannot switch to another account.
"""

from __future__ import annotations

from typing import Any

from ngris.services._base import AsyncBaseService, BaseService, path_id, put_ref


def _invite_body(email: str, role_uuid: str) -> dict[str, Any]:
    body: dict[str, Any] = {"email": email}
    put_ref(body, "role", role_uuid, _extra=1)
    return body


class OrganizationsService(BaseService):
    """Sync accounts service."""

    def list(self) -> list[dict[str, Any]]:
        """The accounts the key's user belongs to (``GET /user/accounts``).

        The key's own account has ``is_active: true``.
        """
        accounts: list[dict[str, Any]] = self._client._get_raw("/user/accounts").get("accounts", [])
        return accounts

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create an account owned by the key's user (``POST /user/accounts``).

        ``data`` needs ``name``. Returns the new account. The key keeps
        acting in its own account.
        """
        account: dict[str, Any] = self._client._post_raw("/user/accounts", data).get("account", {})
        return account

    def get(self) -> dict[str, Any]:
        """The key's own account (``GET /account``)."""
        account: dict[str, Any] = self._client._get_raw("/account").get("account", {})
        return account

    def update(self, name: str) -> None:
        """Rename the key's own account (``PUT /account/settings``)."""
        self._client._put_void("/account/settings", {"name": name})

    def list_members(self, page: int = 1, page_size: int = 50) -> dict[str, Any]:
        """One page of the key's account members (``GET /account/members``).

        Returns ``members``, ``seats``, ``total``, ``page`` and ``page_size``.
        """
        return self._client._get_raw("/account/members", params={"page": page, "page_size": page_size})

    def invite_member(self, email: str, role_uuid: str) -> dict[str, Any]:
        """Invite ``email`` into the key's account with the role ``role_uuid``
        (``POST /account/invites``). Returns the invitation."""
        resp = self._client._post_raw("/account/invites", _invite_body(email, role_uuid))
        invitation: dict[str, Any] = resp.get("invitation", {})
        return invitation

    def remove_member(self, user_uuid: str) -> None:
        """Remove a member from the key's account
        (``DELETE /account/members/{user_uuid}``)."""
        self._client._delete_void(f"/account/members/{path_id(user_uuid, 'user_uuid')}")


class AsyncOrganizationsService(AsyncBaseService):
    """Async accounts service."""

    async def list(self) -> list[dict[str, Any]]:
        accounts: list[dict[str, Any]] = (await self._client._get_raw("/user/accounts")).get("accounts", [])
        return accounts

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        account: dict[str, Any] = (await self._client._post_raw("/user/accounts", data)).get("account", {})
        return account

    async def get(self) -> dict[str, Any]:
        account: dict[str, Any] = (await self._client._get_raw("/account")).get("account", {})
        return account

    async def update(self, name: str) -> None:
        await self._client._put_void("/account/settings", {"name": name})

    async def list_members(self, page: int = 1, page_size: int = 50) -> dict[str, Any]:
        return await self._client._get_raw("/account/members", params={"page": page, "page_size": page_size})

    async def invite_member(self, email: str, role_uuid: str) -> dict[str, Any]:
        resp = await self._client._post_raw("/account/invites", _invite_body(email, role_uuid))
        invitation: dict[str, Any] = resp.get("invitation", {})
        return invitation

    async def remove_member(self, user_uuid: str) -> None:
        await self._client._delete_void(f"/account/members/{path_id(user_uuid, 'user_uuid')}")
