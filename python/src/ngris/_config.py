from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Union


# HTTP verbs we'll auto-retry by default. POST/PATCH are excluded because
# they aren't idempotent and an unsuccessful first attempt may have already
# committed a side effect (created an endpoint, charged a card). Callers
# who use idempotency keys can override `retry_on_methods` to include POST.
_DEFAULT_IDEMPOTENT_METHODS = ("GET", "HEAD", "PUT", "DELETE", "OPTIONS")

# Headers the SDK reserves and will refuse to override from extra_headers
# — letting the caller override these accidentally would leak/corrupt auth.
RESERVED_HEADERS = frozenset({"authorization", "x-api-key", "user-agent"})


@dataclass
class NgrisConfig:
    """Client configuration. Most fields fall back to environment variables
    so users don't have to thread credentials through code paths.

    Env vars (used when the corresponding field is empty/default):
      NGRIS_API_KEY    → api_key
      NGRIS_BASE_URL   → base_url
    """

    base_url: str = ""
    # api_key is excluded from auto-repr to keep it out of tracebacks,
    # ipython auto-display, and any logger.debug(self) output.
    api_key: str = field(default="", repr=False)
    # Per-phase timeouts. Single-value `timeout` is kept for back-compat
    # with the previous public API; if it's set non-zero it wins over the
    # phase-specific values.
    timeout: float = 30.0
    connect_timeout: float = 5.0
    read_timeout: float = 30.0
    write_timeout: float = 30.0
    pool_timeout: float = 5.0
    max_retries: int = 3
    retry_on_status: tuple[int, ...] = (429, 500, 502, 503, 504)
    # Limit retries to safe verbs by default. POST is intentionally
    # excluded — see _DEFAULT_IDEMPOTENT_METHODS.
    retry_on_methods: tuple[str, ...] = _DEFAULT_IDEMPOTENT_METHODS
    backoff_factor: float = 0.5
    backoff_max: float = 10.0
    default_page_size: int = 50
    # Hard cap on auto-pagination so a misbehaving server can't trap the
    # SDK in a near-infinite loop (total=999999, items=[1] per page).
    max_pages: int = 1000
    # HTTP/2 on by default — `httpx[http2]` is a hard dependency so the
    # required `h2` package ships with every install. Multiplexed streams
    # eliminate head-of-line blocking on concurrent service calls and
    # paginated list requests. Set http2=False to force HTTP/1.1.
    http2: bool = True
    # TLS verification. Defaults to True; set to False ONLY for self-signed
    # development environments. Accepts a path to a CA bundle for custom
    # trust roots.
    verify: Union[bool, str] = True
    # httpx connection-pool sizing. Defaults follow httpx but are exposed
    # so high-throughput callers can tune without monkey-patching.
    pool_max_connections: int = 100
    pool_max_keepalive: int = 20
    extra_headers: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Env-var fallbacks. Only apply when the field was left at its
        # default — explicit values from code always win.
        if not self.api_key:
            self.api_key = os.environ.get("NGRIS_API_KEY", "")
        if not self.base_url:
            self.base_url = os.environ.get("NGRIS_BASE_URL", "https://api.ngris.io")
