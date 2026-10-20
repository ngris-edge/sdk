"""``users.me()`` / ``users.update()`` parse what GET / PUT /user really answer.

api-server answers both with ``selfProfile`` (api/user_security_handlers.go):
the caller's identity only — no plan, limits, balance or ``updated_at`` — and
it leaves out ``role`` for the default "user" role, ``pending_email`` unless an
email change awaits confirmation, and ``last_login_at`` before the first
sign-in. ``User`` required those, so both calls raised ``ValidationError``.
"""

from __future__ import annotations

import json

import pytest
import respx

from ngris import AsyncNgris, Ngris
from ngris.models.users import User, UserProfile

BASE = "https://api.example.test"
USER = "019a0000-1111-7222-8333-444455556666"

# A normal user: every field selfProfile always sends, none of the omitempty ones.
_MINIMAL = {
    "id": 1024,
    "uuid": USER,
    "username": "ada",
    "full_name": "",
    "email": "ada@example.com",
    "email_verified": True,
    "status": "active",
    "mfa_enabled": False,
    "created_at": "2026-01-01T00:00:00Z",
}

# Every field selfProfile can send (an admin with a pending email change).
_FULL = {
    **_MINIMAL,
    "full_name": "Ada Lovelace",
    "pending_email": "ada@new.example.com",
    "role": "admin",
    "mfa_enabled": True,
    "last_login_at": "2026-10-19T08:00:00Z",
    "organization_id": 3,
    "current_org_context": 3,
}


@pytest.fixture
def client() -> Ngris:
    with Ngris(api_key="ngris_test", base_url=BASE, max_retries=0, http2=False) as c:
        yield c


class TestUserProfile:
    @respx.mock
    def test_me_parses_a_normal_user(self, client: Ngris) -> None:
        respx.get(f"{BASE}/user").respond(200, json=_MINIMAL)
        p = client.users.me()
        assert isinstance(p, UserProfile)
        assert p.uuid == USER and p.username == "ada" and p.full_name == ""
        assert p.role == "user"  # left out by the API for the default role
        assert p.pending_email is None and p.last_login_at is None

    @respx.mock
    def test_me_parses_every_field(self, client: Ngris) -> None:
        respx.get(f"{BASE}/user").respond(200, json=_FULL)
        p = client.users.me()
        assert p.role == "admin" and p.full_name == "Ada Lovelace" and p.mfa_enabled is True
        assert p.pending_email == "ada@new.example.com"
        assert p.last_login_at is not None and p.last_login_at.year == 2026

    @respx.mock
    def test_update_returns_the_profile(self, client: Ngris) -> None:
        route = respx.put(f"{BASE}/user").respond(200, json={**_MINIMAL, "full_name": "Ada"})
        p = client.users.update({"full_name": "Ada"})
        assert json.loads(route.calls.last.request.content) == {"full_name": "Ada"}
        assert isinstance(p, UserProfile) and p.full_name == "Ada"

    def test_user_still_refuses_the_profile(self) -> None:
        # Why the methods changed model: the full User needs the plan fields.
        with pytest.raises(ValueError):
            User.model_validate(_MINIMAL)

    def test_has_valid_payment_method_is_none_when_not_sent(self) -> None:
        user = User.model_validate({
            "username": "ada", "email": "ada@example.com", "role": "user", "plan": "team", "status": "active",
            "max_tunnels": 1, "max_endpoints": 1, "max_connections": 1, "bandwidth_limit": 0,
            "mfa_enabled": False, "balance_cents": 0,
            "created_at": "2026-01-01T00:00:00Z", "updated_at": "2026-01-01T00:00:00Z",
        })
        assert user.has_valid_payment_method is None


@respx.mock
async def test_async_me_and_update() -> None:
    respx.get(f"{BASE}/user").respond(200, json=_MINIMAL)
    respx.put(f"{BASE}/user").respond(200, json={**_MINIMAL, "full_name": "Ada"})
    async with AsyncNgris(api_key="ngris_test", base_url=BASE, max_retries=0, http2=False) as c:
        me = await c.users.me()
        updated = await c.users.update({"full_name": "Ada"})
    assert isinstance(me, UserProfile) and me.role == "user"
    assert isinstance(updated, UserProfile) and updated.full_name == "Ada"
