"""``auth.login`` / ``auth.mfa_verify`` against api-server's real answers.

- ``/auth/login`` with MFA on answers ``mfa_required`` with an
  ``mfa_challenge_token`` and a short user (id / uuid / username / email /
  role), no token.
- ``/auth/mfa`` takes ``{mfa_challenge_token, token}`` (preferred) or the
  legacy ``{username, password, token}``, and answers the session token as
  ``access_token`` with the same short user.
- ``/auth/login`` without MFA answers ``token`` and the full sign-in user
  (api-server ``sessionUser``).
"""

from __future__ import annotations

import json

import pytest
import respx

from ngris import AsyncNgris, Ngris
from ngris.models.auth import LoginResponse, LoginUser
from ngris.models.users import User

BASE = "https://api.example.test"
USER = "019a0000-1111-7222-8333-444455556666"

_SHORT_USER = {"id": 7, "uuid": USER, "username": "alice", "email": "alice@example.com", "role": "user"}

# api-server's sessionUser (api/handlers.go), every field it sends.
_SESSION_USER = {
    "id": 7,
    "uuid": USER,
    "username": "alice",
    "email": "alice@example.com",
    "email_verified": True,
    "role": "user",
    "status": "active",
    "mfa_enabled": False,
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": "2026-01-02T00:00:00Z",
    "plan": "team",
    "plan_id": 3,
    "max_tunnels": 10,
    "max_endpoints": 25,
    "max_connections": 100,
    "bandwidth_limit": 0,
    "request_limit": 0,
    "allowed_protocols": "http,tcp",
    "allowed_regions": "",
    "allow_organizations": False,
    "balance_cents": 0,
    "active_account_id": 12,
    "active_account_uuid": "019a1111-2222-7333-8444-555566667777",
    "active_account_name": "Alice",
}

_MFA_REQUIRED = {
    "success": False,
    "mfa_required": True,
    "mfa_challenge_token": "challenge-abc",
    "mfa_expires_in": 300,
    "message": "MFA verification required",
    "user": _SHORT_USER,
}

_MFA_OK = {
    "success": True,
    "access_token": "session-jwt",
    "expires_at": "2026-10-21T00:00:00Z",
    "expires_in": 86400,
    "user": _SHORT_USER,
}


@pytest.fixture
def client() -> Ngris:
    with Ngris(api_key="ngris_test", base_url=BASE, max_retries=0, http2=False) as c:
        yield c


def _body(route: respx.Route) -> object:
    return json.loads(route.calls.last.request.content)


class TestLoginAnswers:
    @respx.mock
    def test_mfa_required_answer_validates(self, client: Ngris) -> None:
        respx.post(f"{BASE}/auth/login").respond(200, json=_MFA_REQUIRED)
        resp = client.auth.login("alice", "pw123")
        assert resp.mfa_required is True
        assert resp.token is None
        assert resp.mfa_challenge_token == "challenge-abc"
        assert resp.mfa_expires_in == 300
        assert isinstance(resp.user, LoginUser)
        assert resp.user.uuid == USER and resp.user.username == "alice"

    @respx.mock
    def test_full_answer_carries_the_full_user(self, client: Ngris) -> None:
        answer = {"token": "session-jwt", "user": _SESSION_USER, "expires_at": "2026-10-21T00:00:00Z"}
        respx.post(f"{BASE}/auth/login").respond(200, json=answer)
        resp = client.auth.login("alice", "pw123")
        assert resp.mfa_required is False and resp.token == "session-jwt"
        assert isinstance(resp.user, User)
        assert resp.user.plan == "team" and resp.user.max_endpoints == 25

    def test_session_user_validates_as_user(self) -> None:
        # Every field User requires is one sessionUser sends (api-server #369 C15
        # dropped last_login_at / has_valid_payment_method / extra_retention_days
        # / fraud_*: none of them is required here).
        user = User.model_validate(_SESSION_USER)
        assert user.last_login_at is None


class TestMFAVerify:
    @respx.mock
    def test_challenge_form(self, client: Ngris) -> None:
        route = respx.post(f"{BASE}/auth/mfa").respond(200, json=_MFA_OK)
        resp = client.auth.mfa_verify(mfa_challenge_token="challenge-abc", token="123456")
        assert _body(route) == {"mfa_challenge_token": "challenge-abc", "token": "123456"}
        assert resp.token == "session-jwt"
        assert isinstance(resp.user, LoginUser) and resp.user.email == "alice@example.com"

    @respx.mock
    def test_legacy_form_still_works(self, client: Ngris) -> None:
        route = respx.post(f"{BASE}/auth/mfa").respond(200, json=_MFA_OK)
        resp = client.auth.mfa_verify("alice", "pw123", "654321")
        assert _body(route) == {"username": "alice", "password": "pw123", "token": "654321"}
        assert resp.token == "session-jwt"

    @respx.mock
    def test_login_then_mfa(self, client: Ngris) -> None:
        respx.post(f"{BASE}/auth/login").respond(200, json=_MFA_REQUIRED)
        route = respx.post(f"{BASE}/auth/mfa").respond(200, json=_MFA_OK)
        first = client.auth.login("alice", "pw123")
        assert first.mfa_required
        second = client.auth.mfa_verify(mfa_challenge_token=first.mfa_challenge_token, token="123456")
        assert _body(route) == {"mfa_challenge_token": "challenge-abc", "token": "123456"}
        assert second.token == "session-jwt"

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"mfa_challenge_token": "c"},  # no code
            {"token": "123456"},  # neither form
            {"username": "alice", "token": "123456"},  # half the legacy form
            {"username": "alice", "password": "pw", "token": "1", "mfa_challenge_token": "c"},  # both forms
        ],
    )
    @respx.mock
    def test_bad_arguments_raise_before_any_request(self, client: Ngris, kwargs: dict[str, str]) -> None:
        route = respx.post(f"{BASE}/auth/mfa").respond(200, json=_MFA_OK)
        with pytest.raises(TypeError):
            client.auth.mfa_verify(**kwargs)
        assert not route.called

    def test_model_reads_access_token_as_token(self) -> None:
        assert LoginResponse.model_validate(_MFA_OK).token == "session-jwt"


@respx.mock
async def test_async_challenge_form() -> None:
    route = respx.post(f"{BASE}/auth/mfa").respond(200, json=_MFA_OK)
    async with AsyncNgris(api_key="ngris_test", base_url=BASE, max_retries=0, http2=False) as c:
        resp = await c.auth.mfa_verify(mfa_challenge_token="challenge-abc", token="123456")
    assert _body(route) == {"mfa_challenge_token": "challenge-abc", "token": "123456"}
    assert resp.token == "session-jwt" and isinstance(resp.user, LoginUser)
