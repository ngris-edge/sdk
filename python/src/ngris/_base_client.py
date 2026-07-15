from __future__ import annotations

import json as _json
import logging
import platform
import random
import time
from typing import Any, Generic, Iterator, TypeVar

import httpx

from ngris._config import NgrisConfig, RESERVED_HEADERS
from ngris._errors import (
    MalformedResponseError,
    NgrisConnectionError,
    NgrisError,
    NotFoundError,
    ServerError,
    _parse_retry_after,
    _raise_for_status,
)
from ngris._logging import (
    extract_request_id,
    http_logger,
    redact_body,
    redact_headers,
    truncate_for_log,
)
from ngris._pagination import AsyncPageIterator, PageIterator, PaginatedResponse
from ngris._version import __version__

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


# Built once per process — `httpx/{ver}` lookup uses httpx's __version__
# so the User-Agent string stays accurate across upgrades.
_USER_AGENT = (
    f"ngris-python/{__version__} "
    f"(httpx/{httpx.__version__}; "
    f"python/{platform.python_version()}; "
    f"{platform.system().lower()})"
)


def _httpx_timeout(cfg: NgrisConfig) -> httpx.Timeout:
    """Build an httpx.Timeout with per-phase values. The legacy single
    `timeout` field still wins if the user explicitly set it differently
    from the default 30.0 — keeps back-compat with the previous API."""
    return httpx.Timeout(
        connect=cfg.connect_timeout,
        read=cfg.read_timeout,
        write=cfg.write_timeout,
        pool=cfg.pool_timeout,
    )


def _httpx_limits(cfg: NgrisConfig) -> httpx.Limits:
    return httpx.Limits(
        max_connections=cfg.pool_max_connections,
        max_keepalive_connections=cfg.pool_max_keepalive,
    )


def _decode_dict(resp: httpx.Response) -> dict[str, Any]:
    """Decode a response body to ``dict[str, Any]`` for the ``_*_raw``
    helpers. Returns ``{}`` for 204/empty bodies and converts list-shaped
    payloads to ``{"items": [...]}`` so callers can rely on a consistent
    shape regardless of what the server returned.
    """
    if resp.status_code == 204 or not resp.content:
        return {}
    try:
        data = resp.json()
    except _json.JSONDecodeError as e:
        raise MalformedResponseError(
            f"server returned non-JSON body (status {resp.status_code}): {resp.text[:200]!r}",
            status_code=resp.status_code,
            headers=dict(resp.headers),
        ) from e
    if isinstance(data, list):
        return {"items": data}
    if not isinstance(data, dict):
        # Scalars come back as {"value": ...} so the call shape stays
        # uniform — better than silently returning a non-dict.
        return {"value": data}
    return data


def _http2_available() -> bool:
    """Returns True if the optional `h2` package is importable. The SDK
    declares httpx[http2] as a hard dep so this should always be True
    for normal installs; the check exists to gracefully degrade in
    environments that pinned httpx without the extra (custom builds,
    monkey-patched test envs).
    """
    try:
        import h2  # noqa: F401
        return True
    except ImportError:
        return False


class BaseClient(Generic[T]):
    """Shared logic for sync and async clients."""

    def __init__(self, config: NgrisConfig) -> None:
        self._config = config
        self._base_url = config.base_url.rstrip("/")

    def _build_headers(self, has_body: bool = False) -> dict[str, str]:
        headers: dict[str, str] = {
            "X-API-Key": self._config.api_key,
            "Accept": "application/json",
            "User-Agent": _USER_AGENT,
        }
        if has_body:
            headers["Content-Type"] = "application/json"
        # Filter reserved headers from extra_headers so a caller can't
        # clobber X-API-Key / Authorization / User-Agent (intentional or
        # not). Logged via dict comprehension; original config dict
        # untouched.
        for k, v in self._config.extra_headers.items():
            if k.lower() in RESERVED_HEADERS:
                continue
            headers[k] = v
        return headers

    def _url(self, path: str) -> str:
        return f"{self._base_url}{path}"

    def _should_retry(self, status_code: int, method: str) -> bool:
        # Retry only when both the status and the verb opt in. Default
        # verb allowlist excludes POST/PATCH for idempotency safety.
        return (
            status_code in self._config.retry_on_status
            and method.upper() in self._config.retry_on_methods
        )

    def _calculate_backoff(self, attempt: int, headers: dict[str, str] | None = None) -> float:
        if headers:
            ra = headers.get("retry-after") or headers.get("Retry-After")
            if ra:
                parsed = _parse_retry_after(ra)
                if parsed is not None:
                    return parsed
        delay = min(self._config.backoff_factor * (2**attempt), self._config.backoff_max)
        jitter = random.uniform(0, delay * 0.1)
        return delay + jitter

    @staticmethod
    def _parse_response(resp: httpx.Response, model: type[BaseModel]) -> Any:
        if resp.status_code == 204 or not resp.content:
            if model is dict:
                return {}
            return model.model_construct()
        try:
            data = resp.json()
        except _json.JSONDecodeError as e:
            # Distinct error class so callers can tell "API replied with
            # garbage" (proxy 5xx HTML, gzipped error, truncated body)
            # from a normal API error response.
            raise MalformedResponseError(
                f"server returned non-JSON body (status {resp.status_code}): {resp.text[:200]!r}",
                status_code=resp.status_code,
                headers=dict(resp.headers),
            ) from e
        if model is dict:
            return data
        return model.model_validate(data)

    @staticmethod
    def _parse_paginated(resp: httpx.Response, item_model: type[T], *, page_size: int = 50) -> PaginatedResponse[T]:
        try:
            data = resp.json()
        except _json.JSONDecodeError as e:
            raise MalformedResponseError(
                f"server returned non-JSON body for paginated request (status {resp.status_code})",
                status_code=resp.status_code,
                headers=dict(resp.headers),
            ) from e
        items = [item_model.model_validate(item) for item in data.get("items", [])]
        # `total` stays None when the server omits it — PaginatedResponse
        # falls back to "iterate until empty page" in that case.
        return PaginatedResponse(
            items=items,
            total=data.get("total"),
            page=data.get("page", 1),
            page_size=data.get("page_size", page_size),
        )


class SyncBaseClient(BaseClient):
    """Sync HTTP client with retry, auth, and JSON helpers."""

    def __init__(self, config: NgrisConfig) -> None:
        super().__init__(config)
        # If http2 was requested but `h2` isn't installed (broken env,
        # custom build), warn and fall back to HTTP/1.1 rather than crash
        # at construction time. Normal installs ship httpx[http2].
        use_http2 = config.http2
        if use_http2 and not _http2_available():
            import warnings
            warnings.warn(
                "ngris: http2=True but the 'h2' package is not installed; "
                "falling back to HTTP/1.1. Install with `pip install httpx[http2]`.",
                RuntimeWarning,
                stacklevel=2,
            )
            use_http2 = False
        self._http = httpx.Client(
            timeout=_httpx_timeout(config),
            limits=_httpx_limits(config),
            verify=config.verify,
            http2=use_http2,
        )

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "SyncBaseClient":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    def _request(self, method: str, path: str, *, body: Any = None, params: dict[str, Any] | None = None) -> httpx.Response:
        headers = self._build_headers(has_body=body is not None)

        # DEBUG-only payload prep: skip the redact/serialize cost in the
        # common INFO-only case. ``isEnabledFor`` is the cheap stdlib check.
        if http_logger.isEnabledFor(logging.DEBUG):
            http_logger.debug(
                "→ %s %s headers=%s body=%s params=%s",
                method, path,
                redact_headers(headers),
                truncate_for_log(redact_body(body)) if body is not None else "",
                params or {},
            )

        for attempt in range(self._config.max_retries + 1):
            t0 = time.monotonic()
            try:
                resp = self._http.request(
                    method,
                    self._url(path),
                    json=body if body is not None else None,
                    params=params,
                    headers=headers,
                )
                duration_ms = (time.monotonic() - t0) * 1000.0
                resp_headers = dict(resp.headers)
                request_id = extract_request_id(resp_headers)
                if (
                    resp.status_code >= 400
                    and self._should_retry(resp.status_code, method)
                    and attempt < self._config.max_retries
                ):
                    backoff = self._calculate_backoff(attempt, resp_headers)
                    http_logger.warning(
                        "← %s %s status=%d request_id=%s — retrying in %.2fs (attempt %d/%d)",
                        method, path, resp.status_code, request_id, backoff,
                        attempt + 1, self._config.max_retries,
                    )
                    time.sleep(backoff)
                    continue
                if resp.status_code >= 400:
                    http_logger.info(
                        "← %s %s status=%d duration_ms=%.1f request_id=%s",
                        method, path, resp.status_code, duration_ms, request_id,
                    )
                    _raise_for_status(resp.status_code, resp.text, resp_headers)
                http_logger.info(
                    "← %s %s status=%d duration_ms=%.1f request_id=%s",
                    method, path, resp.status_code, duration_ms, request_id,
                )
                return resp
            except httpx.ConnectError as e:
                # Connect errors are always safe to retry — the request
                # never reached the server. Read errors mid-flight are
                # NOT auto-retried (could have side effects).
                if attempt < self._config.max_retries:
                    backoff = self._calculate_backoff(attempt)
                    http_logger.warning(
                        "× %s %s connect_error=%s — retrying in %.2fs (attempt %d/%d)",
                        method, path, e, backoff,
                        attempt + 1, self._config.max_retries,
                    )
                    time.sleep(backoff)
                    continue
                http_logger.error("× %s %s connect_error=%s (giving up)", method, path, e)
                raise NgrisConnectionError(str(e)) from e
            except NgrisError:
                # Already a typed SDK error from _raise_for_status — let
                # it through unchanged.
                raise
            except (httpx.HTTPError, httpx.InvalidURL) as e:
                # Other httpx-level failures (DNS, TLS, malformed URL)
                # surface as connection errors, not generic NgrisError.
                http_logger.error("× %s %s transport_error=%s", method, path, e)
                raise NgrisConnectionError(str(e)) from e

        raise NgrisError("max retries exceeded")

    def _get(self, path: str, **kw: Any) -> httpx.Response:
        return self._request("GET", path, **kw)

    def _post(self, path: str, **kw: Any) -> httpx.Response:
        return self._request("POST", path, **kw)

    def _put(self, path: str, **kw: Any) -> httpx.Response:
        return self._request("PUT", path, **kw)

    def _delete(self, path: str, **kw: Any) -> httpx.Response:
        return self._request("DELETE", path, **kw)

    def _get_json(self, path: str, model: type[T], **kw: Any) -> T:
        resp = self._get(path, **kw)
        return self._parse_response(resp, model)  # type: ignore[return-value]

    def _get_json_or_none(self, path: str, model: type[T], **kw: Any) -> T | None:
        try:
            return self._get_json(path, model, **kw)
        except NotFoundError:
            return None

    def _post_json(self, path: str, body: Any, model: type[T], **kw: Any) -> T:
        resp = self._post(path, body=body, **kw)
        return self._parse_response(resp, model)  # type: ignore[return-value]

    def _put_json(self, path: str, body: Any, model: type[T], **kw: Any) -> T:
        resp = self._put(path, body=body, **kw)
        return self._parse_response(resp, model)  # type: ignore[return-value]

    # ── Raw JSON helpers ──────────────────────────────────────────────
    # For endpoints that return free-form JSON we don't (yet) model
    # strictly. Returns ``dict[str, Any]`` straight from json(); skips
    # Pydantic parsing to avoid the "abstract type" tug-of-war that
    # ``model=dict`` used to require.
    def _get_raw(self, path: str, **kw: Any) -> dict[str, Any]:
        return _decode_dict(self._get(path, **kw))

    def _post_raw(self, path: str, body: Any, **kw: Any) -> dict[str, Any]:
        return _decode_dict(self._post(path, body=body, **kw))

    def _put_raw(self, path: str, body: Any, **kw: Any) -> dict[str, Any]:
        return _decode_dict(self._put(path, body=body, **kw))

    # ── Void helpers ──────────────────────────────────────────────────
    # For endpoints whose response we genuinely don't care about (close,
    # cancel, rate, verify, etc.). Sends the request and discards the
    # body. Distinct from ``_*_raw`` so the caller's intent shows up at
    # the call site.
    def _post_void(self, path: str, body: Any = None, **kw: Any) -> None:
        self._post(path, body=body, **kw)

    def _put_void(self, path: str, body: Any = None, **kw: Any) -> None:
        self._put(path, body=body, **kw)

    def _get_void(self, path: str, **kw: Any) -> None:
        self._get(path, **kw)

    def _delete_void(self, path: str, **kw: Any) -> None:
        try:
            self._delete(path, **kw)
        except NotFoundError:
            pass

    def _get_page(
        self,
        path: str,
        model: type[T],
        *,
        page: int = 1,
        page_size: int | None = None,
        params: dict[str, Any] | None = None,
    ) -> PaginatedResponse[T]:
        ps = page_size or self._config.default_page_size
        qp: dict[str, Any] = {"page": page, "page_size": ps}
        if params:
            qp.update(params)
        resp = self._get(path, params=qp)
        return self._parse_paginated(resp, model, page_size=ps)

    def _autopage(
        self,
        path: str,
        model: type[T],
        *,
        page_size: int | None = None,
        params: dict[str, Any] | None = None,
    ) -> Iterator[T]:
        ps = page_size or self._config.default_page_size

        def fetch_page(p: int, _ps: int) -> PaginatedResponse[T]:
            return self._get_page(path, model, page=p, page_size=_ps, params=params)

        return PageIterator(fetch_page, page_size=ps, max_pages=self._config.max_pages)


class AsyncBaseClient(BaseClient):
    """Async HTTP client with retry, auth, and JSON helpers."""

    def __init__(self, config: NgrisConfig) -> None:
        super().__init__(config)
        # Same h2 graceful fallback as SyncBaseClient.
        use_http2 = config.http2
        if use_http2 and not _http2_available():
            import warnings
            warnings.warn(
                "ngris: http2=True but the 'h2' package is not installed; "
                "falling back to HTTP/1.1. Install with `pip install httpx[http2]`.",
                RuntimeWarning,
                stacklevel=2,
            )
            use_http2 = False
        self._http = httpx.AsyncClient(
            timeout=_httpx_timeout(config),
            limits=_httpx_limits(config),
            verify=config.verify,
            http2=use_http2,
        )

    async def close(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> "AsyncBaseClient":
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.close()

    async def _request(self, method: str, path: str, *, body: Any = None, params: dict[str, Any] | None = None) -> httpx.Response:
        import asyncio

        headers = self._build_headers(has_body=body is not None)

        if http_logger.isEnabledFor(logging.DEBUG):
            http_logger.debug(
                "→ %s %s headers=%s body=%s params=%s",
                method, path,
                redact_headers(headers),
                truncate_for_log(redact_body(body)) if body is not None else "",
                params or {},
            )

        for attempt in range(self._config.max_retries + 1):
            t0 = time.monotonic()
            try:
                resp = await self._http.request(
                    method,
                    self._url(path),
                    json=body if body is not None else None,
                    params=params,
                    headers=headers,
                )
                duration_ms = (time.monotonic() - t0) * 1000.0
                resp_headers = dict(resp.headers)
                request_id = extract_request_id(resp_headers)
                if (
                    resp.status_code >= 400
                    and self._should_retry(resp.status_code, method)
                    and attempt < self._config.max_retries
                ):
                    backoff = self._calculate_backoff(attempt, resp_headers)
                    http_logger.warning(
                        "← %s %s status=%d request_id=%s — retrying in %.2fs (attempt %d/%d)",
                        method, path, resp.status_code, request_id, backoff,
                        attempt + 1, self._config.max_retries,
                    )
                    await asyncio.sleep(backoff)
                    continue
                if resp.status_code >= 400:
                    http_logger.info(
                        "← %s %s status=%d duration_ms=%.1f request_id=%s",
                        method, path, resp.status_code, duration_ms, request_id,
                    )
                    _raise_for_status(resp.status_code, resp.text, resp_headers)
                http_logger.info(
                    "← %s %s status=%d duration_ms=%.1f request_id=%s",
                    method, path, resp.status_code, duration_ms, request_id,
                )
                return resp
            except httpx.ConnectError as e:
                if attempt < self._config.max_retries:
                    backoff = self._calculate_backoff(attempt)
                    http_logger.warning(
                        "× %s %s connect_error=%s — retrying in %.2fs (attempt %d/%d)",
                        method, path, e, backoff,
                        attempt + 1, self._config.max_retries,
                    )
                    await asyncio.sleep(backoff)
                    continue
                http_logger.error("× %s %s connect_error=%s (giving up)", method, path, e)
                raise NgrisConnectionError(str(e)) from e
            except NgrisError:
                raise
            except (httpx.HTTPError, httpx.InvalidURL) as e:
                http_logger.error("× %s %s transport_error=%s", method, path, e)
                raise NgrisConnectionError(str(e)) from e

        raise NgrisError("max retries exceeded")

    async def _get(self, path: str, **kw: Any) -> httpx.Response:
        return await self._request("GET", path, **kw)

    async def _post(self, path: str, **kw: Any) -> httpx.Response:
        return await self._request("POST", path, **kw)

    async def _put(self, path: str, **kw: Any) -> httpx.Response:
        return await self._request("PUT", path, **kw)

    async def _delete(self, path: str, **kw: Any) -> httpx.Response:
        return await self._request("DELETE", path, **kw)

    async def _get_json(self, path: str, model: type[T], **kw: Any) -> T:
        resp = await self._get(path, **kw)
        return self._parse_response(resp, model)  # type: ignore[return-value]

    async def _get_json_or_none(self, path: str, model: type[T], **kw: Any) -> T | None:
        try:
            return await self._get_json(path, model, **kw)
        except NotFoundError:
            return None

    async def _post_json(self, path: str, body: Any, model: type[T], **kw: Any) -> T:
        resp = await self._post(path, body=body, **kw)
        return self._parse_response(resp, model)  # type: ignore[return-value]

    async def _put_json(self, path: str, body: Any, model: type[T], **kw: Any) -> T:
        resp = await self._put(path, body=body, **kw)
        return self._parse_response(resp, model)  # type: ignore[return-value]

    async def _get_raw(self, path: str, **kw: Any) -> dict[str, Any]:
        return _decode_dict(await self._get(path, **kw))

    async def _post_raw(self, path: str, body: Any, **kw: Any) -> dict[str, Any]:
        return _decode_dict(await self._post(path, body=body, **kw))

    async def _put_raw(self, path: str, body: Any, **kw: Any) -> dict[str, Any]:
        return _decode_dict(await self._put(path, body=body, **kw))

    async def _post_void(self, path: str, body: Any = None, **kw: Any) -> None:
        await self._post(path, body=body, **kw)

    async def _put_void(self, path: str, body: Any = None, **kw: Any) -> None:
        await self._put(path, body=body, **kw)

    async def _get_void(self, path: str, **kw: Any) -> None:
        await self._get(path, **kw)

    async def _delete_void(self, path: str, **kw: Any) -> None:
        try:
            await self._delete(path, **kw)
        except NotFoundError:
            pass

    async def _get_page(
        self,
        path: str,
        model: type[T],
        *,
        page: int = 1,
        page_size: int | None = None,
        params: dict[str, Any] | None = None,
    ) -> PaginatedResponse[T]:
        ps = page_size or self._config.default_page_size
        qp: dict[str, Any] = {"page": page, "page_size": ps}
        if params:
            qp.update(params)
        resp = await self._get(path, params=qp)
        return self._parse_paginated(resp, model, page_size=ps)

    def _autopage(
        self,
        path: str,
        model: type[T],
        *,
        page_size: int | None = None,
        params: dict[str, Any] | None = None,
    ) -> AsyncPageIterator[T]:
        ps = page_size or self._config.default_page_size

        async def fetch_page(p: int, _ps: int) -> PaginatedResponse[T]:
            return await self._get_page(path, model, page=p, page_size=_ps, params=params)

        return AsyncPageIterator(fetch_page, page_size=ps, max_pages=self._config.max_pages)


# Re-export ServerError so callers don't have to reach into _errors directly
# (used in the JSON-decode branch above for the docstring/typing).
__all__ = [
    "BaseClient",
    "SyncBaseClient",
    "AsyncBaseClient",
    "ServerError",
]
