"""Public ids (ngris API, 2026-10): every resource is addressed by its uuid.

These tests pin, for every service method that takes a resource id:

  - the uuid goes into the path / body exactly as given, with no warning;
  - a legacy integer id still works (the API accepts it until its
    integer-id sunset) but emits a DeprecationWarning;
  - request bodies send ``<x>_uuid`` for a uuid and the legacy ``<x>_id``
    only for an integer;
  - response models parse both the window shape (uuid + integer) and the
    post-sunset shape (uuid only, no integer ``id`` / ``*_id``).
"""

from __future__ import annotations

import json
import warnings
from collections.abc import Callable
from typing import Any

import pytest
import respx

from ngris import AsyncNgris, Ngris
from ngris.models import (
    APIKey,
    AuthToken,
    Certificate,
    ClientCA,
    CustomTemplate,
    Domain,
    Endpoint,
    EndpointClient,
    EndpointRole,
    FirewallPolicy,
    MTLSConfig,
    Plan,
    RateLimitRule,
    RoutingRule,
    SSOConfig,
    TrafficLog,
    TrafficPolicy,
    Tunnel,
    User,
    UserPlan,
)

BASE = "https://api.example.test"

EP = "019bb1e4-e785-77d2-9966-c3cff31d0a0e"
TUNNEL = "019ab73a-b951-7031-aea5-1435da834122"
KEY = "019acd48-a137-7170-bd06-ce3f21e42972"
TOKEN = "019ae915-a554-7fc4-aea3-9c9ce2dd2976"
CA = "019af8a2-4b16-70ea-8090-9f63343250c8"
REQ = "019b1d33-2ca9-7bd2-b322-1330190fd290"
ASSIGN = "019b230b-86f2-701a-8001-a15a433823c1"
PROVIDER = "019b407c-8a46-7001-897f-343e36ba8939"
CLIENT = "019b4b9d-d300-736b-8601-153b3d9f70ee"
ROLE = "019b5fc1-0eb5-7dd8-a0e9-a575428f890d"
FW_POLICY = "019c32cb-35d7-786f-b2c5-d108951e23d8"
FW_COND = "019c4790-e565-733a-8f1b-52bc76befe65"
RL_RULE = "019b344f-6477-7b07-8dac-7d370474eab1"
ROUTING = "019b8b02-732f-7d67-b36a-271ec6e8d5fa"
SSO = "019af662-7814-75fe-ac3c-b767d84325a9"
TEMPLATE = "019b0817-a55a-7007-b556-eea4fe532a62"
POLICY = "019b74e7-6fe8-7784-9d8a-9b7f9cb99a89"
RULE = "019b7fe5-336a-7789-aeab-182ddfcd5711"
LOG = "019ba303-954b-796c-bf40-f33a26697f74"
USER = "019a52c2-ca1e-78ba-ab5c-50362cc29134"
ACCOUNT = "019a68b9-1a79-7820-a884-41f554aba6bd"
DOMAIN = "019bd08f-98db-71b2-8e54-f518d319f111"
CERT = "019be236-c4fb-72c2-b153-1eefef23705b"


@pytest.fixture
def client() -> Ngris:
    return Ngris(api_key="ngris_test", base_url=BASE, max_retries=0)


# (call, method, path) for every service method that puts a resource id in
# the path. ``call(client, id)`` invokes the method with that id in the slot
# under test (other path ids are uuids).
PATH_CASES: list[tuple[str, Callable[[Ngris, Any], Any], str, str]] = [
    ("tunnels.get", lambda c, i: c.tunnels.get(i), "GET", "/tunnels/{}"),
    ("api_keys.delete_api_key", lambda c, i: c.api_keys.delete_api_key(i), "DELETE", "/keys/api/{}"),
    ("api_keys.delete_auth_token", lambda c, i: c.api_keys.delete_auth_token(i), "DELETE", "/keys/auth/{}"),
    ("client_cas.get", lambda c, i: c.client_cas.get(i), "GET", "/client-cas/{}"),
    ("client_cas.delete", lambda c, i: c.client_cas.delete(i), "DELETE", "/client-cas/{}"),
    ("dedicated_ips.cancel_request", lambda c, i: c.dedicated_ips.cancel_request(i), "POST",
     "/dedicated-ips/requests/{}/cancel"),
    ("dedicated_ips.release", lambda c, i: c.dedicated_ips.release(i), "POST", "/dedicated-ips/{}/release"),
    ("endpoint_oauth.get_provider", lambda c, i: c.endpoint_oauth.get_provider(EP, i), "GET",
     f"/endpoints/{EP}/oauth/providers/{{}}"),
    ("endpoint_oauth.update_provider", lambda c, i: c.endpoint_oauth.update_provider(EP, i, {}), "PUT",
     f"/endpoints/{EP}/oauth/providers/{{}}"),
    ("endpoint_oauth.delete_provider", lambda c, i: c.endpoint_oauth.delete_provider(EP, i), "DELETE",
     f"/endpoints/{EP}/oauth/providers/{{}}"),
    ("endpoint_oauth.toggle_provider", lambda c, i: c.endpoint_oauth.toggle_provider(EP, i), "PUT",
     f"/endpoints/{EP}/oauth/providers/{{}}/toggle"),
    ("endpoint_rbac.update_client", lambda c, i: c.endpoint_rbac.update_client(EP, i, {}), "PUT",
     f"/endpoints/{EP}/rbac/clients/{{}}"),
    ("endpoint_rbac.delete_client", lambda c, i: c.endpoint_rbac.delete_client(EP, i), "DELETE",
     f"/endpoints/{EP}/rbac/clients/{{}}"),
    ("endpoint_rbac.update_role", lambda c, i: c.endpoint_rbac.update_role(EP, i, {}), "PUT",
     f"/endpoints/{EP}/rbac/roles/{{}}"),
    ("endpoint_rbac.delete_role", lambda c, i: c.endpoint_rbac.delete_role(EP, i), "DELETE",
     f"/endpoints/{EP}/rbac/roles/{{}}"),
    ("firewall.get_rate_limit", lambda c, i: c.firewall.get_rate_limit(i), "GET", "/firewall/rate-limits/{}"),
    ("firewall.update_rate_limit", lambda c, i: c.firewall.update_rate_limit(i, {}), "PUT",
     "/firewall/rate-limits/{}"),
    ("firewall.delete_rate_limit", lambda c, i: c.firewall.delete_rate_limit(i), "DELETE",
     "/firewall/rate-limits/{}"),
    ("routing_rules.delete", lambda c, i: c.routing_rules.delete(EP, i), "DELETE",
     f"/endpoints/{EP}/routing-rules/{{}}"),
    ("sso.delete", lambda c, i: c.sso.delete(i), "DELETE", "/sso/config/{}"),
    ("sso.test", lambda c, i: c.sso.test(i), "POST", "/sso/config/{}/test"),
    ("templates.delete", lambda c, i: c.templates.delete(i), "DELETE", "/templates/{}"),
    ("traffic_policies.get", lambda c, i: c.traffic_policies.get(EP, i), "GET", f"/endpoints/{EP}/policies/{{}}"),
    ("traffic_policies.delete", lambda c, i: c.traffic_policies.delete(EP, i), "DELETE",
     f"/endpoints/{EP}/policies/{{}}"),
    ("traffic_policies.create_rule", lambda c, i: c.traffic_policies.create_rule(EP, i, {}), "POST",
     f"/endpoints/{EP}/policies/{{}}/rules"),
    ("traffic_policies.delete_rule (rule)", lambda c, i: c.traffic_policies.delete_rule(EP, POLICY, i), "DELETE",
     f"/endpoints/{EP}/policies/{POLICY}/rules/{{}}"),
    ("traffic.get_log", lambda c, i: c.traffic.get_log(i), "GET", "/traffic/logs/{}"),
    ("traffic.replay_log", lambda c, i: c.traffic.replay_log(i), "POST", "/traffic/logs/{}/replay"),
    ("traffic.analyze_log", lambda c, i: c.traffic.analyze_log(i), "POST", "/traffic/logs/{}/analyze"),
]

_TUNNEL_JSON = {
    "uuid": TUNNEL,
    "user_uuid": USER,
    "name": "prod-api",
    "type": "http",
    "local_address": "127.0.0.1:8080",
    "status": "active",
    "agent_count": 1,
    "created_at": "2026-04-20T09:00:00Z",
    "updated_at": "2026-04-29T11:00:00Z",
}
_CA_JSON = {"uuid": CA, "user_uuid": USER, "name": "corp-ca"}


def _respond(route: respx.Route, name: str, method: str) -> None:
    if name == "tunnels.get":
        route.respond(200, json=_TUNNEL_JSON)
    elif name == "client_cas.get":
        route.respond(200, json=_CA_JSON)
    elif method == "DELETE":
        route.respond(204)
    else:
        route.respond(200, json={"ok": True})


@pytest.mark.parametrize("name,call,method,path", PATH_CASES, ids=[c[0] for c in PATH_CASES])
@respx.mock
def test_path_takes_uuid_without_warning(client: Ngris, name: str, call: Any, method: str, path: str) -> None:
    uid = "019c5ff6-43ed-7d5b-ad5f-758b187dceed"
    route = respx.route(method=method, url=BASE + path.format(uid))
    _respond(route, name, method)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        call(client, uid)
    assert route.called


@pytest.mark.parametrize("name,call,method,path", PATH_CASES, ids=[c[0] for c in PATH_CASES])
@respx.mock
def test_path_legacy_int_still_works_with_warning(
    client: Ngris, name: str, call: Any, method: str, path: str
) -> None:
    route = respx.route(method=method, url=BASE + path.format(42))
    _respond(route, name, method)
    with pytest.warns(DeprecationWarning, match="integer ids are deprecated"):
        call(client, 42)
    assert route.called


def test_firewall_policy_ids_were_always_uuids(client: Ngris) -> None:
    """Firewall policy / condition ids are uuid strings: no warning, path as given."""
    with respx.mock:
        get = respx.get(f"{BASE}/firewall/policies/{FW_POLICY}").respond(200, json={"id": FW_POLICY})
        cond = respx.delete(f"{BASE}/firewall/policies/{FW_POLICY}/conditions/{FW_COND}").respond(204)
        with warnings.catch_warnings():
            warnings.simplefilter("error", DeprecationWarning)
            client.firewall.get_policy(FW_POLICY)
            client.firewall.delete_condition(FW_POLICY, FW_COND)
        assert get.called and cond.called


def _body(route: respx.Route) -> dict[str, Any]:
    return json.loads(route.calls.last.request.content)


class TestAuthTokenBody:
    @respx.mock
    def test_endpoint_and_tunnel_uuid(self, client: Ngris) -> None:
        route = respx.post(f"{BASE}/keys/auth").respond(200, json={"uuid": TOKEN, "token": "et_at_x"})
        with warnings.catch_warnings():
            warnings.simplefilter("error", DeprecationWarning)
            tok = client.api_keys.create_auth_token("ci", EP, tunnel_uuid=TUNNEL)
        assert _body(route) == {"description": "ci", "endpoint_uuid": EP, "tunnel_uuid": TUNNEL}
        assert tok["uuid"] == TOKEN

    @respx.mock
    def test_legacy_endpoint_id_kwarg(self, client: Ngris) -> None:
        route = respx.post(f"{BASE}/keys/auth").respond(200, json={"uuid": TOKEN, "token": "et_at_x"})
        # 0.1 docs example: endpoint_id="184" (a numeric string) — sent as the
        # legacy integer.
        with pytest.warns(DeprecationWarning):
            client.api_keys.create_auth_token(description="ci", endpoint_id="184")
        assert _body(route) == {"description": "ci", "endpoint_id": 184}

    @respx.mock
    def test_endpoint_id_kwarg_with_a_uuid(self, client: Ngris) -> None:
        route = respx.post(f"{BASE}/keys/auth").respond(200, json={"uuid": TOKEN, "token": "et_at_x"})
        with pytest.warns(DeprecationWarning, match="endpoint_id= is deprecated"):
            client.api_keys.create_auth_token(description="ci", endpoint_id=EP)
        assert _body(route) == {"description": "ci", "endpoint_uuid": EP}

    def test_both_names_is_an_error(self, client: Ngris) -> None:
        with pytest.raises(TypeError):
            client.api_keys.create_auth_token("ci", EP, endpoint_id=EP)

    @respx.mock
    def test_unbound_token(self, client: Ngris) -> None:
        route = respx.post(f"{BASE}/keys/auth").respond(200, json={"uuid": TOKEN, "token": "et_at_x"})
        client.api_keys.create_auth_token("dev")
        assert _body(route) == {"description": "dev"}


class TestUsersUpdate:
    @respx.mock
    def test_update_puts_own_profile(self, client: Ngris) -> None:
        route = respx.put(f"{BASE}/user").respond(200, json=_USER_JSON)
        with warnings.catch_warnings():
            warnings.simplefilter("error", DeprecationWarning)
            u = client.users.update({"full_name": "Ada"})
        assert _body(route) == {"full_name": "Ada"}
        assert u.uuid == USER

    @respx.mock
    def test_legacy_user_id_form(self, client: Ngris) -> None:
        route = respx.put(f"{BASE}/user").respond(200, json=_USER_JSON)
        with pytest.warns(DeprecationWarning, match="update\\(user_id, data\\)"):
            client.users.update("1024", {"full_name": "Ada"})
        assert _body(route) == {"full_name": "Ada"}


class TestDomainsUpdate:
    @respx.mock
    def test_update_returns_the_ok_body(self, client: Ngris) -> None:
        respx.put(f"{BASE}/domains/self/{DOMAIN}").respond(200, json={"ok": True})
        assert client.domains.update(DOMAIN, {"provider": "manual"}) == {"ok": True}


_USER_JSON = {
    "uuid": USER,
    "username": "ada",
    "email": "ada@example.com",
    "role": "user",
    "plan": "team",
    "status": "active",
    "max_tunnels": 10,
    "max_endpoints": 25,
    "max_connections": 100,
    "bandwidth_limit": 0,
    "mfa_enabled": False,
    "balance_cents": 0,
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": "2026-01-01T00:00:00Z",
}


class TestModelsParsePostSunsetShapes:
    """After the sunset responses carry no integer ids; every model the
    services validate must still parse."""

    def test_endpoint(self) -> None:
        ep = Endpoint.model_validate({
            "uuid": EP, "user_uuid": USER, "account_uuid": ACCOUNT, "domain_uuid": DOMAIN,
            "certificate_uuid": CERT, "subdomain": "api", "protocol": "unified", "is_custom": False,
            "status": "active", "mtls_mode": "disabled",
            "created_at": "2026-01-12T00:00:00Z", "updated_at": "2026-01-12T00:00:00Z",
        })
        assert ep.id is None and ep.domain_uuid == DOMAIN and ep.certificate_uuid == CERT

    def test_window_shape_keeps_integers(self) -> None:
        ep = Endpoint.model_validate({
            "id": 184, "uuid": EP, "user_id": 1024, "user_uuid": USER, "domain_id": 3, "domain_uuid": DOMAIN,
            "subdomain": "api", "protocol": "unified", "is_custom": False, "status": "active",
            "mtls_mode": "disabled", "created_at": "2026-01-12T00:00:00Z", "updated_at": "2026-01-12T00:00:00Z",
        })
        assert ep.id == 184 and ep.uuid == EP

    def test_tunnel(self) -> None:
        t = Tunnel.model_validate(_TUNNEL_JSON)
        assert t.uuid == TUNNEL and t.id is None

    def test_others(self) -> None:
        assert Certificate.model_validate({
            "uuid": CERT, "domain_uuid": DOMAIN, "name": "c", "is_active": True, "is_default": False,
            "acme_issued": False, "created_at": "2026-01-21T00:00:00Z", "updated_at": "2026-01-21T00:00:00Z",
        }).domain_uuid == DOMAIN
        assert ClientCA.model_validate(_CA_JSON).uuid == CA
        assert MTLSConfig.model_validate({"mode": "required", "ca_uuids": [CA]}).ca_uuids == [CA]
        assert Domain.model_validate({
            "uuid": DOMAIN, "account_uuid": ACCOUNT, "name": "example.com", "plan_access": "all",
            "is_active": True, "status": "active",
            "created_at": "2026-01-18T00:00:00Z", "updated_at": "2026-01-18T00:00:00Z",
        }).id is None
        assert RoutingRule.model_validate({
            "uuid": ROUTING, "endpoint_uuid": EP, "name": "r", "priority": 1, "target_agent_id": "a",
            "enabled": True, "created_at": "2026-01-04T00:00:00Z", "updated_at": "2026-01-04T00:00:00Z",
        }).uuid == ROUTING
        assert SSOConfig.model_validate({
            "uuid": SSO, "account_uuid": ACCOUNT, "email_domain": "example.com", "provider_type": "oidc",
            "client_id": "oidc-client", "status": "active",
        }).account_uuid == ACCOUNT
        assert CustomTemplate.model_validate({
            "uuid": TEMPLATE, "user_uuid": USER, "type": "404", "content": "<h1/>", "is_active": True,
            "created_at": "2025-12-10T00:00:00Z",
        }).uuid == TEMPLATE
        assert TrafficPolicy.model_validate({
            "uuid": POLICY, "endpoint_uuid": EP, "name": "p", "enabled": True, "priority": 100,
            "created_at": "2025-12-31T00:00:00Z", "updated_at": "2025-12-31T00:00:00Z",
        }).uuid == POLICY
        assert TrafficLog.model_validate({"uuid": LOG, "endpoint_uuid": EP}).uuid == LOG
        assert RateLimitRule.model_validate({
            "uuid": RL_RULE, "endpoint_uuid": EP, "name": "rl", "requests_per_window": 60,
            "window_size_seconds": 60, "action": "block", "status": "active", "priority": 1,
        }).uuid == RL_RULE
        assert FirewallPolicy.model_validate({
            "id": FW_POLICY, "uuid": FW_POLICY, "user_uuid": USER, "name": "f", "priority": 1,
            "action": "block", "enabled": True,
            "created_at": "2026-02-06T00:00:00Z", "updated_at": "2026-02-06T00:00:00Z",
        }).uuid == FW_POLICY
        assert EndpointClient.model_validate({
            "uuid": CLIENT, "endpoint_uuid": EP, "identifier": "ada", "display_name": "Ada", "status": "active",
        }).uuid == CLIENT
        assert EndpointRole.model_validate({
            "uuid": ROLE, "endpoint_uuid": EP, "name": "admin", "priority": 1, "is_default": False,
        }).uuid == ROLE
        assert APIKey.model_validate({
            "uuid": KEY, "user_uuid": USER, "key": "ngris_…", "description": "ci",
            "created_at": "2025-11-29T00:00:00Z",
        }).uuid == KEY
        assert AuthToken.model_validate({
            "uuid": TOKEN, "user_uuid": USER, "endpoint_uuid": EP, "token": "et_at_…", "description": "ci",
            "status": "active", "created_at": "2025-12-04T00:00:00Z",
        }).endpoint_uuid == EP
        assert User.model_validate(_USER_JSON).uuid == USER
        assert UserPlan.model_validate({"slug": "team", "default_domain_uuid": DOMAIN}).slug == "team"
        assert Plan.model_validate({
            "slug": "team", "name": "Team", "price_monthly": 10, "price_yearly": 100, "max_endpoints": 25,
            "max_tunnels": 25, "max_connections": 100, "max_bandwidth": 0, "is_purchasable": True,
        }).id is None


class TestAsync:
    @respx.mock
    async def test_async_paths_and_bodies(self) -> None:
        async with AsyncNgris(api_key="ngris_test", base_url=BASE, max_retries=0) as c:
            get = respx.get(f"{BASE}/tunnels/{TUNNEL}").respond(200, json=_TUNNEL_JSON)
            mint = respx.post(f"{BASE}/keys/auth").respond(200, json={"uuid": TOKEN, "token": "t"})
            cert = respx.put(f"{BASE}/endpoints/{EP}/certificate").respond(200, json={"ok": True})
            checkout = respx.post(f"{BASE}/billing/checkout").respond(200, json={"url": "https://pay/x"})
            with warnings.catch_warnings():
                warnings.simplefilter("error", DeprecationWarning)
                t = await c.tunnels.get(TUNNEL)
                await c.api_keys.create_auth_token("ci", EP)
                await c.endpoints.assign_certificate(EP, CERT)
                await c.billing.checkout("team")
            assert t.uuid == TUNNEL and get.called
            assert _body(mint) == {"description": "ci", "endpoint_uuid": EP}
            assert _body(cert) == {"use_default": False, "certificate_uuid": CERT}
            assert _body(checkout) == {"plan": "team", "interval": "monthly"}

            legacy = respx.delete(f"{BASE}/keys/auth/7").respond(204)
            with pytest.warns(DeprecationWarning):
                await c.api_keys.delete_auth_token(7)  # type: ignore[arg-type]
            assert legacy.called


def test_bool_is_not_a_legacy_id() -> None:
    from ngris.services._base import _is_legacy_int

    assert _is_legacy_int(7) and _is_legacy_int("7")
    assert not _is_legacy_int(True)
    assert not _is_legacy_int(EP)
    assert not _is_legacy_int("٣")  # non-ASCII digit


@respx.mock
def test_traffic_policies_list_unwraps_policies(client: Ngris) -> None:
    respx.get(f"{BASE}/endpoints/{EP}/policies").respond(
        200, json={"policies": [{"uuid": POLICY, "name": "edge", "priority": 100}]}
    )
    assert client.traffic_policies.list(EP) == [{"uuid": POLICY, "name": "edge", "priority": 100}]


@respx.mock
def test_templates_activate_sends_type(client: Ngris) -> None:
    route = respx.post(f"{BASE}/templates/{TEMPLATE}/activate").respond(200)
    assert client.templates.activate(TEMPLATE, type="firewall") is None
    assert _body(route) == {"type": "firewall"}


@respx.mock
def test_promote_returns_the_minimal_confirmation(client: Ngris) -> None:
    respx.post(f"{BASE}/endpoints/{EP}/promote").respond(
        200, json={"endpoint_id": 184, "uuid": EP, "endpoint_uuid": EP, "ephemeral": False}
    )
    ep = client.endpoints.promote(EP)
    assert ep["endpoint_uuid"] == EP and ep["ephemeral"] is False
