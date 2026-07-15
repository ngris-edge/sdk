# ngris

Python SDK for the [Ngris](https://ngris.io) edge gateway platform. Manage endpoints, tunnels, domains, certificates, traffic policies, routing rules, firewall, billing, organizations, and more.

## Install

```bash
pip install ngris
```

## Two ways to use the SDK

The SDK has two distinct surfaces:

1. **`Ngris` (management client)** — manage endpoints, domains, traffic policies, billing, etc. via the HTTP API. Stateless, thread-safe, no subprocess.
2. **`ngris.connect()` (tunnel control)** — open a live tunnel from your Python process by spawning the bundled agent binary. Returns a handle to the running tunnel.

## Quick Start (live tunnel)

```python
import ngris

# Spawn an agent, get a public URL pointing at localhost:8080.
# Reads NGRIS_API_KEY from env (or pass api_key=...).
with ngris.connect(8080) as t:
    print(t.public_url)   # https://abc123.ngris.io
    # ... your app on :8080 is now reachable from the internet
# Agent killed automatically on exit; auth token revoked.
```

```python
# Custom hostname (must be a domain registered to your account)
t = ngris.connect(8080, hostname="hello.example.com")
print(t.public_url)
t.close()

# TCP / UDP tunnel
t = ngris.connect(5432, protocol="tcp")
```

The agent binary (`ngris-agent` or `easytunnel-agent`) must be on PATH or
pointed at via `NGRIS_AGENT_BIN`. Get it from
[ngris.io/install](https://ngris.io/install).

## Quick Start (management client)

```python
from ngris import Ngris

client = Ngris(api_key="ngris_...")

# List endpoints
for ep in client.endpoints.list_all():
    print(ep.uuid, ep.public_url)

# Create an endpoint. Endpoints are protocol-agnostic and region-less:
# protocol is chosen per-tunnel by the agent, and region is a property of
# the serving tunnel (GeoDNS steers traffic), so neither is sent on create.
ep = client.endpoints.create({
    "subdomain": "myapp",
})

# Add a routing rule
client.routing_rules.create(ep.uuid, {
    "name": "api-route",
    "priority": 10,
    "conditions": [{"condition_type": "path", "pattern": "/api/*"}],
    "target_agent_id": "api-agent",
    "enabled": True,
})

# Add a traffic policy
client.traffic_policies.create(ep.uuid, {
    "name": "rate-limit",
    "priority": 10,
    "enabled": True,
})

# Register a custom domain
domain = client.domains.create({"name": "example.com", "provider": "cloudflare"})

client.close()
```

## Async

```python
from ngris import AsyncNgris

async with AsyncNgris(api_key="ngris_...") as client:
    endpoints = await client.endpoints.list()
    async for ep in client.endpoints.list_all():
        print(ep.uuid, ep.public_url)
```

## Authentication

Get an API key from the Ngris dashboard or via the API:

```bash
curl -X POST https://api.ngris.io/keys/api \
  -H "Authorization: Bearer <jwt>" \
  -d '{"description": "my SDK key"}'
```

## Error Handling

```python
from ngris import Ngris, NotFoundError, RateLimitError

client = Ngris(api_key="ngris_...")

try:
    ep = client.endpoints.get("nonexistent-uuid")
except NotFoundError as e:
    # Every NgrisError carries the server's X-Request-ID — quote it in
    # support tickets so we can grep server logs deterministically.
    print(f"Not found (request_id={e.request_id})")
except RateLimitError as e:
    print(f"Rate limited, retry after {e.retry_after}s")
```

## Webhooks

Verify Ngris-signed webhooks before acting on them. The server signs
every webhook with HMAC-SHA256 over the raw request body and delivers
the hex digest in `X-Webhook-Signature`.

```python
from ngris import verify_signature, parse_event, WebhookSignatureError

@app.post("/webhooks/ngris")
async def ngris_webhook(request):
    raw_body = await request.body()         # raw bytes — DO NOT re-encode
    sig = request.headers["X-Webhook-Signature"]
    try:
        event = parse_event(
            raw_body, sig, secret=os.environ["NGRIS_WH_SECRET"],
            max_age_seconds=300,            # reject replays older than 5min
        )
    except WebhookSignatureError:
        return Response(status_code=400)

    if event["event"] == "endpoint.created":
        ...
```

`verify_signature` is the lower-level primitive if you'd rather parse
the JSON yourself. Both use a constant-time compare and raise
`WebhookSignatureError` (a subclass of `NgrisError`) on any mismatch.

## Logging

The SDK logs through stdlib `logging` under the `ngris` hierarchy and
does not call `basicConfig` itself. Headers (`X-API-Key`, `Authorization`,
`Cookie`) and credential-shaped body fields (`password`, `token`,
`api_key`, …) are redacted before any log call.

```python
import logging

# Per-request INFO line: method, path, status, duration, request_id.
logging.getLogger("ngris.http").setLevel(logging.INFO)

# DEBUG adds redacted request headers + bodies. Bodies are capped at 4KB.
logging.getLogger("ngris.http").setLevel(logging.DEBUG)

logging.basicConfig(format="%(levelname)s %(name)s %(message)s")
```

## API Coverage

| Service | Methods |
|---------|---------|
| `client.auth` | login, forgot_password, reset_password, generate_token |
| `client.users` | get, update, get_plan, get_entitlements, get_usage |
| `client.billing` | checkout, get_subscription, cancel, list_invoices, get_balance |
| `client.endpoints` | list, create, get, delete, get_settings, update_settings, get_health |
| `client.endpoint_oauth` | list_providers, create_provider, toggle_provider |
| `client.endpoint_rbac` | list_clients, create_client, list_roles, create_role, list_memberships |
| `client.traffic_policies` | list, create, get, update, delete, create_rule, delete_rule |
| `client.routing_rules` | list, create, get, update, delete |
| `client.firewall` | list_policies, create_policy, list_rate_limits, create_rate_limit |
| `client.domains` | list_available, create, update, delete, list_dns_records |
| `client.certificates` | list, upload, delete, download |
| `client.api_keys` | list_api_keys, create_api_key, list_auth_tokens |
| `client.client_cas` | list, create, get, delete, get_mtls, update_mtls |
| `client.tunnels` | list, get |
| `client.traffic` | list_logs, get_log, get_metrics, smart_search |
| `client.organizations` | list, create, get, update, list_members, invite_member |
| `client.sso` | list, create, get, update, delete, test |
| `client.dedicated_ips` | list, list_requests, create_request, release |
| `client.ai_chat` | list_sessions, create_session, chat |
| `client.support` | list_tickets, create_ticket, reply, close_ticket |
| `client.templates` | list, upload, delete, activate |
| `client.regions` | list_plans, list_regions, list_addons |

## Requirements

- Python 3.10+
- httpx >= 0.27
- pydantic >= 2.0

## Versioning & Changelog

Releases are tracked in [CHANGELOG.md](CHANGELOG.md). The SDK follows
[Semantic Versioning](https://semver.org/): while pre-1.0, MINOR bumps
(`0.X.0`) signal breaking changes and PATCH (`0.x.Y`) signals
backwards-compatible additions and fixes. Every breaking change ships
with a one-line migration note in the changelog entry.

## License

MIT
