"""``accounts`` and ``support`` call routes that exist; ``ai_chat`` is gone.

- ``accounts`` maps to api-server's account routes: ``/user/accounts``
  (list, create) and the active-account scope ``/account``,
  ``/account/settings``, ``/account/members``, ``/account/invites``. An API key
  always runs in its own account, so those take no account id.
- ``support`` calls ngris-support's public ticket API
  (``https://support.ngris.com/api/support/tickets*``) with the same API key.
- ``ai_chat`` is removed: ai-gateway serves ``/v1/ai/sessions`` to session
  JWTs only, never to an API key.
"""

from __future__ import annotations

import json
import warnings

import pytest
import respx

from ngris import AsyncNgris, Ngris

BASE = "https://api.example.test"
DESK = "https://support.ngris.com"
ACCOUNT = "019a1111-2222-7333-8444-555566667777"
ROLE = "019b5fc1-0eb5-7dd8-a0e9-a575428f890d"
MEMBER = "019a0000-1111-7222-8333-444455556666"
TICKET = "019c7777-8888-7999-8aaa-bbbbccccdddd"


@pytest.fixture
def client() -> Ngris:
    with Ngris(api_key="ngris_test", base_url=BASE, max_retries=0, http2=False) as c:
        yield c


def _body(route: respx.Route) -> object:
    return json.loads(route.calls.last.request.content)


class TestAccounts:
    @respx.mock
    def test_list_unwraps_accounts(self, client: Ngris) -> None:
        respx.get(f"{BASE}/user/accounts").respond(
            200,
            json={
                "accounts": [{"uuid": ACCOUNT, "name": "Acme", "is_active": True}],
                "active_account_id": 5,
                "active_account_uuid": ACCOUNT,
            },
        )
        assert client.accounts.list() == [{"uuid": ACCOUNT, "name": "Acme", "is_active": True}]

    @respx.mock
    def test_create_posts_to_user_accounts(self, client: Ngris) -> None:
        route = respx.post(f"{BASE}/user/accounts").respond(201, json={"account": {"uuid": ACCOUNT, "name": "Lab"}})
        assert client.accounts.create({"name": "Lab"}) == {"uuid": ACCOUNT, "name": "Lab"}
        assert _body(route) == {"name": "Lab"}

    @respx.mock
    def test_get_reads_the_keys_account(self, client: Ngris) -> None:
        respx.get(f"{BASE}/account").respond(200, json={"account": {"uuid": ACCOUNT, "name": "Acme"}})
        assert client.accounts.get() == {"uuid": ACCOUNT, "name": "Acme"}

    @respx.mock
    def test_update_renames_via_settings(self, client: Ngris) -> None:
        route = respx.put(f"{BASE}/account/settings").respond(200, json={"success": True})
        assert client.accounts.update("Acme Labs") is None
        assert _body(route) == {"name": "Acme Labs"}

    @respx.mock
    def test_list_members_returns_the_page(self, client: Ngris) -> None:
        page = {
            "members": [{"user_uuid": MEMBER}],
            "seats": {"unlimited": True},
            "total": 1,
            "page": 2,
            "page_size": 10,
        }
        route = respx.get(f"{BASE}/account/members").respond(200, json=page)
        assert client.accounts.list_members(page=2, page_size=10) == page
        assert dict(route.calls.last.request.url.params) == {"page": "2", "page_size": "10"}

    @respx.mock
    def test_invite_member_sends_email_and_role_uuid(self, client: Ngris) -> None:
        route = respx.post(f"{BASE}/account/invites").respond(201, json={"invitation": {"uuid": "inv-1"}})
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            assert client.accounts.invite_member("a@b.co", ROLE) == {"uuid": "inv-1"}
        assert _body(route) == {"email": "a@b.co", "role_uuid": ROLE}

    @respx.mock
    def test_remove_member_deletes_by_user_uuid(self, client: Ngris) -> None:
        route = respx.delete(f"{BASE}/account/members/{MEMBER}").respond(200, json={"success": True})
        assert client.accounts.remove_member(MEMBER) is None
        assert route.called

    def test_dead_methods_are_gone(self, client: Ngris) -> None:
        # DELETE /account refuses API keys (interactive session only), and an
        # API key cannot switch accounts.
        assert not hasattr(client.accounts, "delete")
        assert not hasattr(client.accounts, "switch")

    @respx.mock
    async def test_async(self) -> None:
        respx.get(f"{BASE}/user/accounts").respond(200, json={"accounts": [{"uuid": ACCOUNT}]})
        route = respx.post(f"{BASE}/account/invites").respond(201, json={"invitation": {"uuid": "inv-1"}})
        async with AsyncNgris(api_key="ngris_test", base_url=BASE, max_retries=0, http2=False) as c:
            assert await c.accounts.list() == [{"uuid": ACCOUNT}]
            assert await c.accounts.invite_member("a@b.co", ROLE) == {"uuid": "inv-1"}
        assert _body(route) == {"email": "a@b.co", "role_uuid": ROLE}


class TestSupport:
    @respx.mock
    def test_calls_the_support_desk_with_the_api_key(self, client: Ngris) -> None:
        route = respx.get(f"{DESK}/api/support/tickets").respond(200, json=[{"uuid": TICKET}])
        assert client.support.list_tickets() == [{"uuid": TICKET}]
        assert route.calls.last.request.headers["x-api-key"] == "ngris_test"

    @respx.mock
    def test_ticket_routes(self, client: Ngris) -> None:
        create = respx.post(f"{DESK}/api/support/tickets").respond(201, json={"uuid": TICKET})
        get = respx.get(f"{DESK}/api/support/tickets/{TICKET}").respond(
            200, json={"ticket": {"uuid": TICKET}, "messages": []}
        )
        close = respx.post(f"{DESK}/api/support/tickets/{TICKET}/close").respond(204)

        data = {"subject": "TLS", "message": "cert not issued", "category": "technical", "priority": "normal"}
        assert client.support.create_ticket(data) == {"uuid": TICKET}
        assert _body(create) == data
        assert client.support.get_ticket(TICKET) == {"ticket": {"uuid": TICKET}, "messages": []}
        assert client.support.close_ticket(TICKET) is None
        assert get.called and close.called

    @respx.mock
    def test_support_base_url_is_configurable(self) -> None:
        route = respx.get("https://support.staging.example/api/support/tickets").respond(200, json=[])
        with Ngris(api_key="k", base_url=BASE, support_base_url="https://support.staging.example/", http2=False) as c:
            assert c.support.list_tickets() == []
        assert route.called

    @respx.mock
    def test_other_services_stay_on_the_api_base(self, client: Ngris) -> None:
        route = respx.get(f"{BASE}/tunnels").respond(200, json={"items": []})
        client.tunnels.list()
        assert route.called

    @respx.mock
    async def test_async(self) -> None:
        route = respx.post(f"{DESK}/api/support/tickets/{TICKET}/messages").respond(201, json={"id": 1})
        async with AsyncNgris(api_key="ngris_test", base_url=BASE, max_retries=0, http2=False) as c:
            await c.support.reply(TICKET, "any update?")
        assert _body(route) == {"message": "any update?"}


def test_ai_chat_is_removed(client: Ngris) -> None:
    assert not hasattr(client, "ai_chat")
