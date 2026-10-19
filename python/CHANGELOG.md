# Changelog

All notable changes to the `ngris` Python SDK are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Versioning policy

While the SDK is pre-1.0 (`0.x.y`):

- **MINOR** (`0.X.0`) — breaking changes. Method renames, removed parameters,
  changed return types, anything that requires user code edits to upgrade.
- **PATCH** (`0.x.Y`) — backwards-compatible additions and bug fixes. New
  methods, new optional parameters, new error subclasses, internal cleanups.

After `1.0.0`, standard SemVer applies: MAJOR for breaking changes, MINOR for
additions, PATCH for fixes.

Every breaking change in a release MUST be listed under a `Changed` or
`Removed` section in the entry below, with a one-line migration note.

---

## [Unreleased]

Nothing yet.

## [0.3.0] — not released yet (traffic-log request ids and filters)

### Added

- `TrafficLog.request_id`: the edge's `X-Request-Id` for the request, the
  value the client got in that response header (`None` on TCP/UDP sessions,
  older entries and some edge-generated error responses).
- `traffic.list_logs()` (sync and async) takes the API's list filters as
  keyword arguments, with the API's names and operators: `request_id`,
  `endpoint_uuid`, `policy_uuid`, `rate_limit_rule_uuid`, `since_uuid`,
  `since` / `until` (RFC 3339 strings or timezone-aware datetimes),
  `time_range`, `search`, `firewall_action`, `rate_action`, and the
  condition-builder dimensions `host`, `path`, `ua`, `method`, `source_ip`,
  `status`, `protocol`, `asn`, `country`, `browser`, `os`, `region`,
  `http_version` — each a value or a list of values, with an optional
  `<dim>_op`. `TrafficLogFilters` (`ngris.services.traffic`) types them. An
  unknown filter raises `TypeError`; an operator a dimension doesn't take, an
  operator without its value, or a naive datetime raises `ValueError`,
  because the API would ignore such a filter and return every entry.

Nothing changes for existing calls: `list_logs()` and
`list_logs(page, page_size)` send exactly what they sent before.

## [0.2.0] — not released yet (public ids)

The ngris API now addresses every resource by its `uuid` (public ids; see
https://ngris.com/docs/public-ids). Integer ids are deprecated: the API
accepts them until its integer-id sunset (2026-11-13 23:59:59 UTC, or
earlier if integer use stays at zero for 7 days) and refuses them after that
with `400 integer_id_unsupported`. Upgrade before the sunset.

### Changed

- Every method that takes a resource id takes the resource's **uuid**
  (a string), and its parameter is renamed accordingly — e.g.
  `tunnels.get(tunnel_uuid)`, `api_keys.delete_auth_token(token_uuid)`,
  `firewall.get_rate_limit(rule_uuid)`, `traffic.get_log(log_uuid)`,
  `endpoint_rbac.update_client(uuid, client_uuid, data)`,
  `traffic_policies.update_rule(endpoint_uuid, policy_uuid, rule_uuid, data)`,
  `dedicated_ips.release(assignment_uuid)`. Migration: pass the `uuid` from
  the list / create response instead of the integer `id`; callers that pass
  the id positionally only change the value, callers that used the old
  keyword names (`provider_id=`, `rule_id=` …) switch to the `*_uuid` name.
  An integer still works until the sunset and emits a `DeprecationWarning`.
- `billing.checkout(plan, interval="monthly", payment_method_id=None)` takes
  the plan's **slug** (`"team"`). Migration: `checkout(plan="team")` instead
  of `checkout(plan_id=2)`; `plan_id=` / a numeric first argument still work
  until the sunset with a `DeprecationWarning`.
- `endpoints.assign_certificate(uuid, certificate_uuid=None, *, use_default=False)`
  sends `certificate_uuid`. Migration: pass the certificate's uuid;
  `certificate_id=` still works until the sunset with a `DeprecationWarning`.
- `api_keys.create_auth_token(description="", endpoint_uuid=None, *, tunnel_uuid=None)`
  sends `endpoint_uuid` / `tunnel_uuid`. Migration: pass the endpoint's uuid;
  `endpoint_id=` still works until the sunset with a `DeprecationWarning`.
  The response carries the token's `uuid`; revoke with it.
- `users.update(data)` updates the caller's own profile with `PUT /user` (the
  old `update(user_id, data)` called a route that does not exist). Migration:
  drop the user id; the two-argument form still works with a
  `DeprecationWarning`.
- `domains.update(uuid, data)` returns the API's `{"ok": true}` body as a dict
  (it used to parse it as a `Domain` and fail).
- Models expose `uuid` and the `*_uuid` reference fields (`user_uuid`,
  `account_uuid`, `endpoint_uuid`, `domain_uuid`, `certificate_uuid`,
  `tunnel_uuid`, `policy_uuid`, `client_uuid`, `role_uuid`, `ca_uuids`,
  `default_domain_uuid` …) and plans their `slug`. Their integer `id` /
  `*_id` fields are now optional and deprecated: the API stops returning them
  at the sunset. Migration: read `uuid` / `*_uuid`.
- Request models: `CreateEndpointRequest.domain_uuid` and
  `UploadCertificateRequest.domain_uuid` replace `domain_id`.
- `templates.upload(type, content, *, active=False)` sends the
  multipart/form-data the API reads (`type`, the page as the `template` file
  part, `active=true`). It used to post JSON, which the API always refused.
  Migration: `upload("not_found", html)` instead of `upload({"type": ...,
  "content": ...})`; `content` is a `str` or `bytes`.
- `endpoints.get_health(uuid)` returns the API's real health shape:
  `HealthStatus` now has `endpoint_uuid`, `has_active_agent`, `uptime_24h`,
  `uptime_7d`, `uptime_30d` (percent), `avg_latency_ms`, `last_check` and
  `recent_checks` (new `HealthCheck` model). The old `status`,
  `uptime_seconds` and datetime `last_check` fields are gone (the call never
  parsed). Migration: read `last_check.status` and the uptime fields.
- **`client.organizations` is renamed `client.accounts`** (ngris has accounts, not
  organizations; no alias). The legacy `organization_id` / `allow_organizations`
  fields are dropped from `User` and `SSOConfig` (unused since accounts).
- `accounts` calls the API's account routes (it called
  `/organization*` routes that do not exist). An API key always acts in its
  own account, so the methods that act on "the account" take no account id:
  `list()` (`GET /user/accounts`, returns the accounts list),
  `create(data)` (`POST /user/accounts`, returns the new account),
  `get()` (`GET /account`), `update(name)` (`PUT /account/settings`),
  `list_members(page=1, page_size=50)` (`GET /account/members`, returns the
  page: `members`, `seats`, `total`, `page`, `page_size`),
  `invite_member(email, role_uuid)` (`POST /account/invites`, returns the
  invitation) and the new `remove_member(user_uuid)`
  (`DELETE /account/members/{user_uuid}`). Migration: drop the `org_id`
  argument; pass `update` the new name and `invite_member` the email and
  role uuid instead of a dict. All results are dicts.
- `support` calls ngris-support's ticket API at `support_base_url` (new
  client option, default `https://support.ngris.com`) under
  `/api/support/tickets`, with the same API key. It used to call
  `/support/tickets` on the API host, which no longer serves them.
  Migration: none; pass `support_base_url=` only for a non-production desk.

### Removed

- `ai_chat` (and the `ChatSession` / `ChatMessage` models). ai-gateway serves
  AI chat to signed-in dashboard sessions only, never to an API key, so no
  call could work. Migration: none; use Iris in the dashboard.
- `accounts.delete()` (was `organizations.delete()`): the API refuses account deletion with an API key
  (interactive dashboard session only). Migration: delete the account in the
  dashboard.
- `accounts.switch()` (was `organizations.switch()`): an API key always acts in its own account and
  cannot switch. Migration: use an API key created in the target account.
- The `Organization`, `OrganizationMember` and `OrganizationInvitation`
  models, which matched no API response. Migration: read the dicts the
  `accounts` methods return.

### Fixed

- The default `base_url` is `https://api.ngris.com/v1`, the management API
  (service paths are joined to it: `GET https://api.ngris.com/v1/endpoints`).
  The old default, `https://api.ngris.io`, never answered, so no call worked
  without an explicit `base_url`. An explicit `base_url=` or
  `NGRIS_BASE_URL` is used as before.
- `auth.generate_token()` no longer fails to parse the `{"token": ...}` reply.
- `traffic_policies.list()` returns the policies from the API's
  `{"policies": [...]}` reply instead of the wrapping dict.
- `firewall.list_conditions(policy_uuid)` returns the conditions from the
  API's `{"conditions": [...]}` reply instead of the wrapping dict.
- `endpoints.promote(uuid)` returns the API's minimal confirmation
  (`uuid`, `endpoint_uuid`, `ephemeral`) as a dict; it used to parse it as a
  full `Endpoint` and fail.
- `templates.activate(template_uuid, type)` sends the `{"type": ...}` body the
  API requires and returns `None` (the API answers 200 with no body); it
  used to send `{}` and always fail.
- `ngris.connect()` revokes its auth token by uuid (falling back to the
  integer id on a server from before the public-id change, without
  surfacing a warning).

## [0.1.0] — 2026-04-29

Initial public release. The SDK exposes two surfaces:

1. **`Ngris` / `AsyncNgris`** — management client for the HTTP API
   (endpoints, tunnels, domains, traffic policies, billing, …).
2. **`ngris.connect()`** — subprocess wrapper that spawns the bundled
   agent binary and returns a live tunnel handle (ngrok-style).

Plus a webhook signature verifier for inbound notifications from Ngris.

### Added

- `Ngris(api_key=..., base_url=...)` and `AsyncNgris(...)` clients with
  service properties: `auth`, `users`, `billing`, `endpoints`,
  `endpoint_oauth`, `endpoint_rbac`, `traffic_policies`, `routing_rules`,
  `firewall`, `domains`, `certificates`, `api_keys`, `client_cas`,
  `tunnels`, `traffic`, `organizations`, `sso`, `dedicated_ips`,
  `ai_chat`, `support`, `templates`, `regions`.
- `ngris.connect(addr, *, protocol="http", hostname=..., api_key=...,
  timeout=30.0)` — opens a live tunnel by spawning the agent binary;
  returns a `Tunnel` context manager that revokes the auth token and
  kills the subprocess on `close()`.
- HTTP/2 transport by default (via `httpx[http2]`); graceful fallback
  to HTTP/1.1 with a `RuntimeWarning` if the optional `h2` package is
  unavailable.
- Configurable retry policy: idempotent verbs only by default
  (`GET`/`HEAD`/`PUT`/`DELETE`/`OPTIONS`), exponential backoff with jitter,
  RFC 7231 `Retry-After` parsing (both delta-seconds and HTTP-date forms).
- Pagination helpers `_get_page` / `_autopage` returning either a
  `PaginatedResponse[T]` page or an `Iterator[T]` / `AsyncPageIterator[T]`
  with a `max_pages` cap to defend against runaway servers.
- Per-tunnel auth-token mint/revoke (`POST /keys/auth`,
  `DELETE /keys/auth/{id}`) routed through the main SDK client so the
  request inherits retry, logging, and error mapping.
- `from ngris import verify_signature, parse_event, WebhookSignatureError`
  — HMAC-SHA256 signature verification for inbound webhooks. Constant-time
  compare; optional freshness check via `max_age_seconds` (default 300).
- Structured logging under the `ngris` / `ngris.http` stdlib loggers.
  INFO logs every request (method, path, status, duration, request_id);
  DEBUG adds redacted headers + body (4 KB cap). Headers
  (`Authorization`, `X-API-Key`, `Cookie`, `Set-Cookie`, `Proxy-Authorization`)
  and body fields (`password`, `token`, `api_key`, `secret`, `client_secret`,
  `private_key`, `access_key`, `refresh_token`) are redacted before any
  log call.
- `NgrisError.request_id` populated from `X-Request-ID` /
  `X-Correlation-ID` response headers and surfaced via `repr()`.
- `MalformedResponseError` distinct subclass for non-JSON response
  bodies (proxy 5xx HTML pages bleeding through, gzip mismatch, etc.).
- `_get_raw` / `_post_raw` / `_put_raw` helpers returning
  `dict[str, Any]` straight from `resp.json()` for endpoints we don't
  model strictly. List responses normalise to `{"items": [...]}`,
  scalars to `{"value": x}`, 204/empty to `{}`.
- `_get_void` / `_post_void` / `_put_void` for endpoints whose response
  body we genuinely don't care about.
- 21 service modules exposing ~140 typed methods, with sync and async
  parity.
- 108 tests covering auth headers, error mapping, retry, pagination,
  async parity, async-only properties (gather, cancellation, async
  pagination), body-shape correctness, logging redaction, webhook
  verification, helper normalisation, tunnel subprocess lifecycle.
- Python SDK examples added next to every curl example in the API
  reference docs (`webapp/web/api/templates/`); a tab UI lets readers
  switch between curl and Python in-place.
- README sections for management client, live tunnel, async, error
  handling, logging, and webhooks.

### Notes for future contributors

- **Body-shape regression tests live in `tests/services/test_body_shapes.py`.**
  Six handler/SDK mismatches were caught during pre-release audit
  (login expecting `username` not `email`, reset expecting `new_password`
  not `password`, checkout `interval` not `billing_period`, support reply
  `message` not `content`, certificate id type, etc). Any new typed-body
  call should add a regression test here so handler `DisallowUnknownFields`
  changes don't break the SDK silently.
- **The agent's stdout regex is `Public URL: ...`.** Changing the agent's
  startup line will break `ngris.connect()`. Keep the two in lockstep —
  the SDK has a test (`tests/test_tunnel.py::TestPublicURLPattern`) that
  pins both the emoji and plain forms.
- **Routes are mechanically aligned.** All 149 unique SDK call shapes
  match a registered route in `api-server/api/routes.go`. New endpoints
  added to the SDK should be added to that route list too — drift is
  caught only at integration-test time.

[Unreleased]: https://github.com/ngris-edge/ngris-python/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ngris-edge/ngris-python/releases/tag/v0.1.0
