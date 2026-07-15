from __future__ import annotations

from email.utils import parsedate_to_datetime
from datetime import datetime, timezone


class NgrisError(Exception):
    """Base exception for all Ngris SDK errors."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        headers: dict[str, str] | None = None,
        request_id: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.headers = headers or {}
        # Server-issued correlation id (X-Request-ID / X-Correlation-ID).
        # Surfaced on every error so users can paste it into bug reports
        # and we can grep server logs deterministically.
        self.request_id = request_id

    def __repr__(self) -> str:
        parts = [self.message]
        if self.status_code is not None:
            parts.append(f"status_code={self.status_code}")
        if self.request_id is not None:
            parts.append(f"request_id={self.request_id!r}")
        return f"{type(self).__name__}({', '.join(parts)})"


class AuthenticationError(NgrisError):
    """401 — Invalid or missing API key."""


class PermissionDeniedError(NgrisError):
    """403 — Authenticated but not authorized."""


class NotFoundError(NgrisError):
    """404 — Resource not found."""


class ValidationError(NgrisError):
    """400/422 — Request validation failed."""


class RateLimitError(NgrisError):
    """429 — Rate limit exceeded."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        headers: dict[str, str] | None = None,
        retry_after: float | None = None,
        request_id: str | None = None,
    ) -> None:
        super().__init__(
            message,
            status_code=status_code,
            headers=headers,
            request_id=request_id,
        )
        self.retry_after = retry_after


class ServerError(NgrisError):
    """5xx — Upstream server error."""


class MalformedResponseError(NgrisError):
    """Server returned a non-JSON or otherwise unparseable body where JSON
    was expected — typically a proxy / load balancer 5xx HTML page bleeding
    through. Distinguished from ServerError so callers can choose to
    retry differently (e.g., fail fast vs. exponential backoff)."""


class NgrisConnectionError(NgrisError):
    """Network-level connection failure."""


def _parse_retry_after(value: str) -> float | None:
    """Parse a Retry-After header value. RFC 7231 allows two formats:
      * delta-seconds: integer number of seconds (e.g. "120")
      * HTTP-date:     RFC 7231 date (e.g. "Wed, 21 Oct 2026 07:28:00 GMT")

    Returns the wait-duration in seconds, or None on parse failure. Never
    returns negative values — past dates clamp to 0.
    """
    value = value.strip()
    if not value:
        return None
    try:
        return max(float(value), 0.0)
    except ValueError:
        pass
    try:
        target = parsedate_to_datetime(value)
        if target is None:
            return None
        if target.tzinfo is None:
            target = target.replace(tzinfo=timezone.utc)
        delta = (target - datetime.now(timezone.utc)).total_seconds()
        return max(delta, 0.0)
    except (TypeError, ValueError):
        return None


def _raise_for_status(status_code: int, body: str, headers: dict[str, str]) -> None:
    """Parse the API error response and raise the appropriate exception."""
    message = body
    # API returns {"error": "message"} — try to extract
    if body.startswith("{"):
        import json

        try:
            data = json.loads(body)
            if isinstance(data, dict) and "error" in data:
                message = data["error"]
        except (json.JSONDecodeError, KeyError):
            pass

    # Local import to avoid a cycle: _logging is a leaf module but it
    # may grow imports of its own later, so keep _errors free of top-level
    # SDK deps.
    from ngris._logging import extract_request_id

    request_id = extract_request_id(headers)
    kw: dict[str, object] = {
        "status_code": status_code,
        "headers": headers,
        "request_id": request_id,
    }

    if status_code == 401:
        raise AuthenticationError(message, **kw)  # type: ignore[arg-type]
    if status_code == 403:
        raise PermissionDeniedError(message, **kw)  # type: ignore[arg-type]
    if status_code == 404:
        raise NotFoundError(message, **kw)  # type: ignore[arg-type]
    if status_code in (400, 422):
        raise ValidationError(message, **kw)  # type: ignore[arg-type]
    if status_code == 429:
        # httpx normalizes header keys to lowercase, but case-insensitive
        # lookup costs nothing and protects against non-httpx wrappers.
        ra = headers.get("retry-after") or headers.get("Retry-After")
        retry_after = _parse_retry_after(ra) if ra else None
        raise RateLimitError(message, retry_after=retry_after, **kw)  # type: ignore[arg-type]
    if status_code >= 500:
        raise ServerError(message, **kw)  # type: ignore[arg-type]

    raise NgrisError(message, **kw)  # type: ignore[arg-type]
