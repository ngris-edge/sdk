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
