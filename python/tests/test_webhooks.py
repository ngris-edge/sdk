"""Tests for the webhook signature verifier.

Security-critical surface, so coverage emphasises *negative* cases —
empty signatures, wrong-length attacks, hex tampering, JSON edge cases —
in addition to the happy path.

The shared fixture builds a payload whose HMAC signature matches the
server's exact scheme: ``hex(HMAC-SHA256(secret, raw_body))``. Any
regression in the algorithm choice (different hash, base64 instead of
hex, signing a re-encoded body) is caught by ``test_round_trip``.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone

import pytest

from ngris import WebhookSignatureError, parse_event, verify_signature


SECRET = "whsec_super_secret_value"


def _sign(body: bytes, secret: str = SECRET) -> str:
    return hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def _now_ts() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@pytest.fixture
def signed_event() -> tuple[bytes, str]:
    body = json.dumps(
        {
            "event": "endpoint.created",
            "timestamp": _now_ts(),
            "data": {"uuid": "abc-123"},
        }
    ).encode()
    return body, _sign(body)


# ─────────────────────────────────────────────────────────────────────
# verify_signature — happy path + every meaningful failure mode
# ─────────────────────────────────────────────────────────────────────


class TestVerifySignature:
    def test_round_trip(self, signed_event) -> None:
        body, sig = signed_event
        # Returns None on success — assert by *not* raising.
        verify_signature(body, sig, SECRET)

    def test_accepts_str_payload(self) -> None:
        body = '{"event":"x"}'
        sig = _sign(body.encode())
        verify_signature(body, sig, SECRET)

    def test_wrong_signature_rejected(self, signed_event) -> None:
        body, _ = signed_event
        bad = "0" * 64  # right length, wrong content
        with pytest.raises(WebhookSignatureError, match="signature mismatch"):
            verify_signature(body, bad, SECRET)

    def test_truncated_signature_rejected(self, signed_event) -> None:
        """Length mismatch must short-circuit *without* falling through
        to compare_digest in a way that leaks timing — but more
        importantly, it must reject."""
        body, sig = signed_event
        with pytest.raises(WebhookSignatureError, match="signature mismatch"):
            verify_signature(body, sig[:-1], SECRET)

    def test_empty_signature_rejected(self, signed_event) -> None:
        body, _ = signed_event
        with pytest.raises(WebhookSignatureError, match="missing signature"):
            verify_signature(body, "", SECRET)

    def test_empty_secret_rejected(self, signed_event) -> None:
        """Caller misconfiguration: empty secret must never accept."""
        body, sig = signed_event
        with pytest.raises(WebhookSignatureError, match="secret is empty"):
            verify_signature(body, sig, "")

    def test_wrong_secret_rejected(self, signed_event) -> None:
        body, sig = signed_event
        with pytest.raises(WebhookSignatureError):
            verify_signature(body, sig, "wrong_secret")

    def test_tampered_body_rejected(self, signed_event) -> None:
        _, sig = signed_event
        tampered = b'{"event":"endpoint.deleted","data":{"uuid":"abc-123"}}'
        with pytest.raises(WebhookSignatureError):
            verify_signature(tampered, sig, SECRET)

    def test_different_secret_with_same_body_rejected(self) -> None:
        body = b'{"event":"x"}'
        sig_a = _sign(body, "secret-a")
        # Signature computed with secret-a must not verify with secret-b.
        with pytest.raises(WebhookSignatureError):
            verify_signature(body, sig_a, "secret-b")

    def test_case_sensitive_hex(self, signed_event) -> None:
        """``hexdigest`` returns lowercase. Uppercase would be byte-different
        even though the bytes are equivalent — we follow the server's
        format strictly. Locks the contract so a future "be friendly,
        accept either case" change has to be a deliberate decision."""
        body, sig = signed_event
        with pytest.raises(WebhookSignatureError):
            verify_signature(body, sig.upper(), SECRET)

    def test_non_bytes_non_str_raises_type_error(self) -> None:
        with pytest.raises(TypeError):
            verify_signature(12345, "deadbeef", SECRET)  # type: ignore[arg-type]


# ─────────────────────────────────────────────────────────────────────
# parse_event — same verification + JSON parse + freshness
# ─────────────────────────────────────────────────────────────────────


class TestParseEvent:
    def test_returns_parsed_dict(self, signed_event) -> None:
        body, sig = signed_event
        event = parse_event(body, sig, SECRET)
        assert event["event"] == "endpoint.created"
        assert event["data"]["uuid"] == "abc-123"

    def test_bad_signature_propagates(self, signed_event) -> None:
        body, _ = signed_event
        with pytest.raises(WebhookSignatureError):
            parse_event(body, "0" * 64, SECRET)

    def test_invalid_json_after_valid_signature(self) -> None:
        """Pathological case: the bytes are signed correctly but happen
        to not be JSON. The verifier must still reject (signature is
        valid, payload isn't usable). This protects callers who
        assume parse_event always returns a dict on success."""
        body = b"not json at all"
        sig = _sign(body)
        with pytest.raises(WebhookSignatureError, match="not valid JSON"):
            parse_event(body, sig, SECRET)

    def test_json_array_rejected(self) -> None:
        """The contract is "JSON object" — an array is technically valid
        JSON but doesn't match the documented event shape."""
        body = b'[{"event":"x"}]'
        sig = _sign(body)
        with pytest.raises(WebhookSignatureError, match="not a JSON object"):
            parse_event(body, sig, SECRET)

    def test_missing_timestamp_skips_age_check(self) -> None:
        body = json.dumps({"event": "x", "data": {}}).encode()
        sig = _sign(body)
        # No timestamp — must not raise even though max_age is set tight.
        event = parse_event(body, sig, SECRET, max_age_seconds=1)
        assert event["event"] == "x"

    def test_old_timestamp_rejected(self) -> None:
        old = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat().replace(
            "+00:00", "Z"
        )
        body = json.dumps(
            {"event": "x", "timestamp": old, "data": {}}
        ).encode()
        sig = _sign(body)
        with pytest.raises(WebhookSignatureError, match="too old"):
            parse_event(body, sig, SECRET, max_age_seconds=300)

    def test_age_check_disabled_with_none(self) -> None:
        old = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat().replace(
            "+00:00", "Z"
        )
        body = json.dumps(
            {"event": "x", "timestamp": old, "data": {}}
        ).encode()
        sig = _sign(body)
        event = parse_event(body, sig, SECRET, max_age_seconds=None)
        assert event["event"] == "x"

    def test_unparseable_timestamp_skips_age_check(self) -> None:
        """If the timestamp field exists but is in some weird format we
        can't parse, fail open — the signature already verified the
        bytes weren't tampered with, so a non-RFC-3339 timestamp is
        more likely a server bug than an attack."""
        body = json.dumps(
            {"event": "x", "timestamp": "not-a-date", "data": {}}
        ).encode()
        sig = _sign(body)
        event = parse_event(body, sig, SECRET, max_age_seconds=1)
        assert event["event"] == "x"

    def test_iso_with_offset_accepted(self) -> None:
        """Servers emit ``...Z``; some proxies rewrite to ``...+00:00``.
        Both must round-trip."""
        ts = (
            datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()  # ends in +00:00 by default
        )
        body = json.dumps({"event": "x", "timestamp": ts, "data": {}}).encode()
        sig = _sign(body)
        event = parse_event(body, sig, SECRET, max_age_seconds=300)
        assert event["timestamp"] == ts


# ─────────────────────────────────────────────────────────────────────
# Public-API smoke — proves the helpers are reachable from `import ngris`
# rather than only from the private module path.
# ─────────────────────────────────────────────────────────────────────


def test_public_api_exports() -> None:
    import ngris

    assert ngris.verify_signature is verify_signature
    assert ngris.parse_event is parse_event
    assert ngris.WebhookSignatureError is WebhookSignatureError
