"""Webhook signature verification.

Ngris signs every outgoing webhook with HMAC-SHA256 over the raw request
body, hex-encoded, and delivers it in the ``X-Webhook-Signature`` header.
The event name travels in ``X-Webhook-Event``. The signed payload is a
JSON object whose top-level fields include ``event``, ``timestamp`` (an
RFC 3339 UTC string), and an event-specific ``data`` object.

Verifying a webhook in your handler::

    from ngris.webhooks import verify_signature, WebhookSignatureError

    @app.post("/ngris/webhooks")
    async def ngris_webhook(request):
        body = await request.body()           # raw bytes — DO NOT re-encode
        sig = request.headers["X-Webhook-Signature"]
        try:
            verify_signature(body, sig, secret=os.environ["NGRIS_WH_SECRET"])
        except WebhookSignatureError:
            return Response(status=400)
        # ... safe to parse and act on the event ...

For replay protection you can use :func:`parse_event` instead, which
parses the JSON body and rejects payloads whose ``timestamp`` is older
than ``max_age_seconds`` (default 5 min)::

    event = parse_event(body, sig, secret, max_age_seconds=300)
    handle(event["event"], event["data"])

Two things every implementation gets wrong, both load-bearing here:

  * **Constant-time compare.** Uses :func:`hmac.compare_digest` so a
    timing side-channel can't leak the expected signature byte by byte.
  * **Raw bytes in, raw bytes signed.** If a framework hands you a
    decoded JSON dict, do NOT re-serialize and pass that — the bytes
    won't match what the server signed (key order, whitespace,
    Unicode escaping all differ). Capture the raw body before the
    framework parses it.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timezone
from typing import Any

from ngris._errors import NgrisError


class WebhookSignatureError(NgrisError):
    """Raised when a webhook signature fails verification.

    Subclass of :class:`NgrisError` so existing ``except NgrisError`` blocks
    catch it. Distinct class so handlers can return 400 specifically for
    bad-signature requests vs. 500 for other failures.
    """


def _to_bytes(payload: bytes | str) -> bytes:
    """Coerce a payload to bytes. Strings are UTF-8 encoded — but the
    caller should really be passing the raw request body bytes; this is
    a guardrail, not a feature.
    """
    if isinstance(payload, bytes):
        return payload
    if isinstance(payload, str):
        return payload.encode("utf-8")
    raise TypeError(
        f"webhook payload must be bytes or str, got {type(payload).__name__}"
    )


def _compute_signature(payload: bytes, secret: str) -> str:
    mac = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256)
    return mac.hexdigest()


def verify_signature(
    payload: bytes | str,
    signature: str,
    secret: str,
) -> None:
    """Verify ``signature`` matches HMAC-SHA256(secret, payload).

    Raises :class:`WebhookSignatureError` on any mismatch — empty
    signature, wrong length, bad hex, or simply incorrect MAC. The
    comparison is constant-time.

    ``payload`` MUST be the raw bytes the server signed. If your web
    framework already parsed the JSON, fetch the raw body from a
    framework-specific hook (FastAPI: ``await request.body()``; Flask:
    ``request.get_data()``; Django: ``request.body``).
    """
    if not signature:
        raise WebhookSignatureError("missing signature")
    if not secret:
        # Misconfiguration: caller passed an empty secret. Raise rather
        # than silently accept any signature against b"".
        raise WebhookSignatureError("webhook secret is empty")

    expected = _compute_signature(_to_bytes(payload), secret)

    # ``compare_digest`` requires equal-length inputs to do its
    # constant-time work — a length mismatch can short-circuit. Guard
    # explicitly so a 4-byte signature doesn't leak that timing info.
    if len(signature) != len(expected):
        raise WebhookSignatureError("signature mismatch")
    if not hmac.compare_digest(signature, expected):
        raise WebhookSignatureError("signature mismatch")


def parse_event(
    payload: bytes | str,
    signature: str,
    secret: str,
    *,
    max_age_seconds: int | None = 300,
) -> dict[str, Any]:
    """Verify the signature, parse the JSON body, and return the event dict.

    ``max_age_seconds`` (default 300, i.e. 5 minutes) caps how old a
    payload's ``timestamp`` field may be before the call rejects it as
    a replay. Pass ``None`` to disable the age check. Payloads that
    don't include a ``timestamp`` field skip the check (the server may
    legitimately omit it for some events).

    Returns the parsed JSON dict with the ``event``, ``timestamp``, and
    ``data`` keys the server emits.
    """
    verify_signature(payload, signature, secret)

    try:
        event = json.loads(_to_bytes(payload))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise WebhookSignatureError(f"webhook body is not valid JSON: {e}") from e

    if not isinstance(event, dict):
        raise WebhookSignatureError("webhook body is not a JSON object")

    if max_age_seconds is not None:
        ts = event.get("timestamp")
        if isinstance(ts, str):
            parsed = _parse_iso8601(ts)
            if parsed is not None:
                age = (datetime.now(timezone.utc) - parsed).total_seconds()
                if age > max_age_seconds:
                    raise WebhookSignatureError(
                        f"webhook payload too old: {age:.0f}s > {max_age_seconds}s"
                    )

    return event


def _parse_iso8601(value: str) -> datetime | None:
    """Parse the server's RFC 3339 UTC timestamp.

    Accepts both ``...Z`` and ``...+00:00`` forms — the server emits
    the trailing ``Z`` form via ``time.Format(time.RFC3339)``, but
    proxies sometimes rewrite it. Returns None on parse failure rather
    than raising, since age-check failure is non-fatal (we just skip
    the freshness check).
    """
    try:
        # ``fromisoformat`` accepts Z since Python 3.11; substitute for
        # 3.10 compatibility.
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        dt = datetime.fromisoformat(value)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


__all__ = [
    "WebhookSignatureError",
    "verify_signature",
    "parse_event",
]
