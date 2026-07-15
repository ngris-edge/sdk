"""Regression tests for SDK body-shape correctness.

These tests pin the *exact* JSON body the SDK sends for routes whose
handler uses ``DisallowUnknownFields()`` — drift would mean unknown-field
errors on the wire, not test failures, which is much harder to debug.

Background: a body-shape sweep against the api-server handlers found
six mismatches that these tests now lock in:

  - ``/auth/login`` wants ``username``, not ``email``
  - ``/auth/reset-password`` wants ``new_password``, not ``password``
  - ``/auth/token`` ignores its body (handler hardcodes the description)
  - ``/billing/checkout`` wants ``interval`` (not ``billing_period``) and
    ``plan_id`` as ``int`` (not ``str``)
  - ``/support/tickets/{uuid}/messages`` wants ``message``, not ``content``
  - ``/endpoints/{uuid}/certificate`` wants ``certificate_id`` as ``int``
    plus a ``use_default`` bool
"""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from ngris import Ngris


@pytest.fixture
def client() -> Ngris:
    return Ngris(api_key="ngris_test", base_url="https://api.example.test")


def _body_of(call) -> dict:
    return json.loads(call.request.content)


class TestAuthBodies:
    @respx.mock
    def test_login_sends_username_not_email(self, client: Ngris) -> None:
        route = respx.post("https://api.example.test/auth/login").respond(
            200, json={"token": "t", "user": None, "mfa_required": False}
        )
        client.auth.login("alice", "pw123")
        body = _body_of(route.calls.last)
        assert body == {"username": "alice", "password": "pw123"}
        # Must not leak old field names: handler uses DisallowUnknownFields.
        assert "email" not in body
        assert "mfa_code" not in body

    @respx.mock
    def test_mfa_verify_body(self, client: Ngris) -> None:
        route = respx.post("https://api.example.test/auth/mfa").respond(
            200, json={"token": "t", "user": None, "mfa_required": False}
        )
        client.auth.mfa_verify("alice", "pw123", "654321")
        assert _body_of(route.calls.last) == {
            "username": "alice",
            "password": "pw123",
            "token": "654321",
        }

    @respx.mock
    def test_reset_password_uses_new_password(self, client: Ngris) -> None:
        route = respx.post("https://api.example.test/auth/reset-password").respond(204)
        client.auth.reset_password("reset-token", "newpw1234")
        body = _body_of(route.calls.last)
        assert body == {"token": "reset-token", "new_password": "newpw1234"}
        assert "password" not in body

    @respx.mock
    def test_generate_token_sends_empty_body(self, client: Ngris) -> None:
        route = respx.post("https://api.example.test/auth/token").respond(
            200, json={"id": 1, "token": "tk"}
        )
        client.auth.generate_token()
        assert _body_of(route.calls.last) == {}


class TestBillingBodies:
    @respx.mock
    def test_checkout_uses_interval_and_int_plan_id(self, client: Ngris) -> None:
        route = respx.post("https://api.example.test/billing/checkout").respond(
            200, json={"session_id": "s", "url": "https://pay/x"}
        )
        client.billing.checkout(plan_id=42, interval="yearly")
        body = _body_of(route.calls.last)
        assert body == {"plan_id": 42, "interval": "yearly"}
        assert isinstance(body["plan_id"], int)
        assert "billing_period" not in body

    @respx.mock
    def test_checkout_optional_payment_method(self, client: Ngris) -> None:
        route = respx.post("https://api.example.test/billing/checkout").respond(
            200, json={"session_id": "s", "url": "https://pay/x"}
        )
        client.billing.checkout(plan_id=1, payment_method_id="pm_abc")
        body = _body_of(route.calls.last)
        assert body == {
            "plan_id": 1,
            "interval": "monthly",
            "payment_method_id": "pm_abc",
        }

    @respx.mock
    def test_validate_coupon_optional_plan(self, client: Ngris) -> None:
        route = respx.post("https://api.example.test/coupons/validate").respond(
            200, json={"valid": True, "message": "ok"}
        )
        client.billing.validate_coupon("SAVE10", plan="pro")
        assert _body_of(route.calls.last) == {"code": "SAVE10", "plan": "pro"}

        client.billing.validate_coupon("SAVE10")
        assert _body_of(route.calls.last) == {"code": "SAVE10"}


class TestSupportBodies:
    @respx.mock
    def test_reply_uses_message_not_content(self, client: Ngris) -> None:
        route = respx.post(
            "https://api.example.test/support/tickets/abc-123/messages"
        ).respond(201, json={"id": 1})
        client.support.reply("abc-123", "thanks for the help")
        body = _body_of(route.calls.last)
        assert body == {"message": "thanks for the help"}
        assert "content" not in body

    @respx.mock
    def test_rate_ticket_optional_comment(self, client: Ngris) -> None:
        route = respx.post(
            "https://api.example.test/support/tickets/abc/rate"
        ).respond(204)
        client.support.rate_ticket("abc", 5, comment="great")
        assert _body_of(route.calls.last) == {"rating": 5, "comment": "great"}

        client.support.rate_ticket("abc", 4)
        assert _body_of(route.calls.last) == {"rating": 4}


class TestEndpointsBodies:
    @respx.mock
    def test_assign_certificate_uses_int_id(self, client: Ngris) -> None:
        route = respx.put(
            "https://api.example.test/endpoints/uuid-1/certificate"
        ).respond(200, json={"ok": True, "certificate_id": 7})
        client.endpoints.assign_certificate("uuid-1", certificate_id=7)
        body = _body_of(route.calls.last)
        assert body == {"use_default": False, "certificate_id": 7}
        assert isinstance(body["certificate_id"], int)

    @respx.mock
    def test_assign_certificate_use_default(self, client: Ngris) -> None:
        route = respx.put(
            "https://api.example.test/endpoints/uuid-1/certificate"
        ).respond(200, json={"ok": True, "certificate_id": None})
        client.endpoints.assign_certificate("uuid-1", use_default=True)
        body = _body_of(route.calls.last)
        # No certificate_id when reverting to default — handler treats
        # missing/zero/use_default as "remove custom cert".
        assert body == {"use_default": True}
        assert "certificate_id" not in body
