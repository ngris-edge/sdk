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
    the plan's slug as ``plan`` (public ids, 2026-10; ``plan_id`` is the
    deprecated integer form)
  - ngris-support's ``/api/support/tickets/{uuid}/messages`` wants
    ``message``, not ``content``
  - ``/endpoints/{uuid}/certificate`` wants ``certificate_uuid`` (the
    certificate's uuid; ``certificate_id`` is the deprecated integer form)
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


CERT_UUID = "019be236-c4fb-72c2-b153-1eefef23705b"


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
            200, json={"token": "tk"}
        )
        tok = client.auth.generate_token()
        assert _body_of(route.calls.last) == {}
        # The handler answers {"token": ...} only.
        assert tok.token == "tk"


class TestBillingBodies:
    @respx.mock
    def test_checkout_uses_interval_and_plan_slug(self, client: Ngris) -> None:
        route = respx.post("https://api.example.test/billing/checkout").respond(
            200, json={"session_id": "s", "url": "https://pay/x"}
        )
        client.billing.checkout(plan="team", interval="yearly")
        body = _body_of(route.calls.last)
        assert body == {"plan": "team", "interval": "yearly"}
        assert "billing_period" not in body
        assert "plan_id" not in body

    @respx.mock
    def test_checkout_optional_payment_method(self, client: Ngris) -> None:
        route = respx.post("https://api.example.test/billing/checkout").respond(
            200, json={"session_id": "s", "url": "https://pay/x"}
        )
        client.billing.checkout("enterprise", payment_method_id="pm_abc")
        body = _body_of(route.calls.last)
        assert body == {
            "plan": "enterprise",
            "interval": "monthly",
            "payment_method_id": "pm_abc",
        }

    @respx.mock
    def test_checkout_legacy_plan_id_still_sent_as_int(self, client: Ngris) -> None:
        route = respx.post("https://api.example.test/billing/checkout").respond(
            200, json={"session_id": "s", "url": "https://pay/x"}
        )
        with pytest.warns(DeprecationWarning, match="plan_id"):
            client.billing.checkout(plan_id=42, interval="yearly")
        body = _body_of(route.calls.last)
        assert body == {"plan_id": 42, "interval": "yearly"}
        assert isinstance(body["plan_id"], int)

        # 0.1 positional form: checkout(42)
        with pytest.warns(DeprecationWarning, match="plan_id"):
            client.billing.checkout(42)
        assert _body_of(route.calls.last) == {"plan_id": 42, "interval": "monthly"}

    def test_checkout_needs_a_plan(self, client: Ngris) -> None:
        with pytest.raises(TypeError):
            client.billing.checkout()
        with pytest.raises(TypeError):
            client.billing.checkout("team", plan_id=2)

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
            "https://support.ngris.com/api/support/tickets/abc-123/messages"
        ).respond(201, json={"id": 1})
        client.support.reply("abc-123", "thanks for the help")
        body = _body_of(route.calls.last)
        assert body == {"message": "thanks for the help"}
        assert "content" not in body

    @respx.mock
    def test_rate_ticket_optional_comment(self, client: Ngris) -> None:
        route = respx.post(
            "https://support.ngris.com/api/support/tickets/abc/rate"
        ).respond(204)
        client.support.rate_ticket("abc", 5, comment="great")
        assert _body_of(route.calls.last) == {"rating": 5, "comment": "great"}

        client.support.rate_ticket("abc", 4)
        assert _body_of(route.calls.last) == {"rating": 4}


class TestEndpointsBodies:
    @respx.mock
    def test_assign_certificate_uses_certificate_uuid(self, client: Ngris) -> None:
        route = respx.put(
            "https://api.example.test/endpoints/uuid-1/certificate"
        ).respond(200, json={"ok": True, "certificate_uuid": CERT_UUID})
        client.endpoints.assign_certificate("uuid-1", CERT_UUID)
        body = _body_of(route.calls.last)
        assert body == {"use_default": False, "certificate_uuid": CERT_UUID}

    @respx.mock
    def test_assign_certificate_legacy_int_id(self, client: Ngris) -> None:
        route = respx.put(
            "https://api.example.test/endpoints/uuid-1/certificate"
        ).respond(200, json={"ok": True, "certificate_id": 7})
        with pytest.warns(DeprecationWarning, match="certificate_id"):
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
        assert "certificate_uuid" not in body


class TestFirewallConditions:
    @respx.mock
    def test_list_conditions_unwraps_the_conditions_key(self, client: Ngris) -> None:
        cond = {
            "id": "019c4790-e565-733a-8f1b-52bc76befe65",
            "uuid": "019c4790-e565-733a-8f1b-52bc76befe65",
            "policy_id": "019c32cb-35d7-786f-b2c5-d108951e23d8",
            "policy_uuid": "019c32cb-35d7-786f-b2c5-d108951e23d8",
            "condition_type": "country",
            "operator": "in",
            "condition_value": "RU, KP",
            "logical_operator": "AND",
            "created_at": "2026-04-29T13:00:00Z",
        }
        respx.get(
            "https://api.example.test/firewall/policies/019c32cb-35d7-786f-b2c5-d108951e23d8/conditions"
        ).respond(200, json={"conditions": [cond]})
        assert client.firewall.list_conditions("019c32cb-35d7-786f-b2c5-d108951e23d8") == [cond]
