"""Structured logging helpers for the Ngris SDK.

The SDK logs through stdlib :mod:`logging` under the ``ngris`` logger
hierarchy (``ngris.http`` for the request layer). It does *not* call
:func:`logging.basicConfig` — apps that don't configure logging see
nothing, which is the documented behaviour for libraries.

To turn it on::

    import logging
    logging.getLogger("ngris").setLevel(logging.DEBUG)
    logging.basicConfig()

Three things need to happen before a request/response can be logged:

1. **Header redaction** — ``X-API-Key`` / ``Authorization`` / ``Cookie``
   carry secrets. They are masked to ``***`` in *all* log output.
2. **Body redaction** — known credential field names (``password``,
   ``token``, ``api_key`` …) are replaced. The redacted dict is also
   capped in size so a 5MB upload doesn't end up in a log file.
3. **Request-ID propagation** — when the server includes an
   ``X-Request-ID`` response header it is attached to both the log
   record and to any :class:`NgrisError` raised, so users can quote it
   in support tickets.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Mapping

# Single logger instance; sub-loggers are derived as needed (ngris.http,
# ngris.tunnel, …) so apps can selectively raise/lower verbosity.
logger = logging.getLogger("ngris")
http_logger = logging.getLogger("ngris.http")

# Header names that must never appear in plaintext in logs. Matched
# case-insensitively. Keep this list conservative — false positives just
# mean a header gets masked, false negatives leak secrets.
_REDACTED_HEADERS = frozenset(
    {
        "authorization",
        "x-api-key",
        "api-key",
        "cookie",
        "set-cookie",
        "proxy-authorization",
    }
)

# JSON body keys that look like credentials. The match is on the key
# *suffix* so ``api_key``, ``new_api_key``, ``user.api_key`` all redact.
_REDACTED_BODY_SUFFIXES = (
    "password",
    "new_password",
    "old_password",
    "token",
    "api_key",
    "apikey",
    "secret",
    "client_secret",
    "private_key",
    "access_key",
    "refresh_token",
)

_REDACTED_PLACEHOLDER = "***"

# Cap per-body log payload to avoid filling a log volume with a stray
# certificate upload or template body. 4 KB is enough for any normal
# request struct in this API.
_MAX_LOGGED_BODY_BYTES = 4096


def redact_headers(headers: Mapping[str, str] | None) -> dict[str, str]:
    """Return a copy of *headers* with secret values replaced by ``***``."""
    if not headers:
        return {}
    out: dict[str, str] = {}
    for k, v in headers.items():
        out[k] = _REDACTED_PLACEHOLDER if k.lower() in _REDACTED_HEADERS else v
    return out


def _looks_secret(key: str) -> bool:
    """True if a JSON body key name should have its value masked."""
    lk = key.lower()
    return any(lk == s or lk.endswith("_" + s) or lk.endswith("." + s) for s in _REDACTED_BODY_SUFFIXES)


def redact_body(body: Any) -> Any:
    """Recursively redact credential-shaped fields in a JSON-ish body.

    Strings/numbers/None are returned untouched; lists and dicts are
    walked. Non-JSON-ish input (e.g. ``bytes``) is rendered to a short
    ``<bytes:N>`` placeholder so logs stay text-only.
    """
    if isinstance(body, dict):
        return {k: (_REDACTED_PLACEHOLDER if _looks_secret(k) else redact_body(v)) for k, v in body.items()}
    if isinstance(body, list):
        return [redact_body(item) for item in body]
    if isinstance(body, (bytes, bytearray)):
        return f"<bytes:{len(body)}>"
    return body


def truncate_for_log(payload: Any) -> str:
    """Render *payload* as a single-line JSON string, truncated for logs.

    Used after :func:`redact_body` — never call this on a raw payload
    containing secrets.
    """
    if payload is None:
        return ""
    try:
        text = json.dumps(payload, default=str, ensure_ascii=False)
    except (TypeError, ValueError):
        text = repr(payload)
    if len(text) > _MAX_LOGGED_BODY_BYTES:
        return text[:_MAX_LOGGED_BODY_BYTES] + f"...<+{len(text) - _MAX_LOGGED_BODY_BYTES}b>"
    return text


def extract_request_id(headers: Mapping[str, str] | None) -> str | None:
    """Pull the server-issued request id out of a response header map.

    Servers in this stack emit ``X-Request-ID``; some proxies rename it
    to ``X-Correlation-ID``. Try both, case-insensitively.
    """
    if not headers:
        return None
    for k, v in headers.items():
        kl = k.lower()
        if kl == "x-request-id" or kl == "x-correlation-id":
            return v
    return None


__all__ = [
    "logger",
    "http_logger",
    "redact_headers",
    "redact_body",
    "truncate_for_log",
    "extract_request_id",
]
