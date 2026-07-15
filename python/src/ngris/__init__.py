"""Ngris Python SDK — manage endpoints, tunnels, domains, traffic policies,
and open live tunnels in-process via `ngris.connect(8080)`."""

from ngris._async_client import AsyncNgris
from ngris._errors import (
    AuthenticationError,
    MalformedResponseError,
    NgrisConnectionError,
    NgrisError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from ngris._sync_client import Ngris
from ngris._tunnel import Tunnel, TunnelStartupError, connect, disconnect
from ngris._version import __version__
from ngris.webhooks import WebhookSignatureError, parse_event, verify_signature

__all__ = [
    "__version__",
    # Management API client
    "Ngris",
    "AsyncNgris",
    # Tunnel control plane (subprocess wrapper around the agent binary)
    "connect",
    "disconnect",
    "Tunnel",
    "TunnelStartupError",
    # Errors
    "NgrisError",
    "AuthenticationError",
    "PermissionDeniedError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
    "MalformedResponseError",
    "NgrisConnectionError",
    # Webhook verification
    "verify_signature",
    "parse_event",
    "WebhookSignatureError",
]
