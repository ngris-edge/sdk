from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import TYPE_CHECKING, Any, Literal, TypedDict, Union

from ngris._pagination import PaginatedResponse
from ngris.models.traffic import TrafficLog
from ngris.services._base import AsyncBaseService, BaseService, path_id

if TYPE_CHECKING:
    from typing_extensions import Unpack

# A condition-builder value: one value, or several (sent comma-separated; with
# no operator the API then matches any of them, i.e. "in").
DimValue = Union[str, int, Sequence[Union[str, int]]]
# Operators of the free-text dimensions (host, path, ua).
TextOp = Literal["equals", "not_equals", "contains", "starts_with", "ends_with", "in", "not_in"]
# Operators of the enumerable dimensions (every other one).
EnumOp = Literal["equals", "not_equals", "in", "not_in"]


class TrafficLogFilters(TypedDict, total=False):
    """Filters of ``traffic.list_logs``: the API's own query parameters.

    See https://ngris.com/docs/api/logs/list. Every filter is optional and
    they combine (AND), always within the API key's account.
    """

    # The X-Request-Id response header the edge returned for one request:
    # finds that request's entry (exact match).
    request_id: str
    endpoint_uuid: str
    policy_uuid: str  # firewall policy
    rate_limit_rule_uuid: str
    since_uuid: str  # only entries newer than this log entry (polling cursor)
    # Time window: RFC 3339 strings, or timezone-aware datetimes.
    since: Union[str, datetime]
    until: Union[str, datetime]
    time_range: Literal["1h", "6h", "24h", "7d"]  # used when since is not given
    search: str  # substring of the path or the client IP
    firewall_action: str
    rate_action: str  # the rate-limit action
    # Condition-builder dimensions, each with an optional <dim>_op operator
    # (default: equals for one value, in for several).
    host: DimValue
    host_op: TextOp
    path: DimValue
    path_op: TextOp
    ua: DimValue  # User-Agent
    ua_op: TextOp
    method: DimValue
    method_op: EnumOp
    source_ip: DimValue
    source_ip_op: EnumOp
    status: DimValue  # codes or classes: 500, "5xx", ["404", "5xx"]
    status_op: EnumOp
    protocol: DimValue  # http, tcp, udp
    protocol_op: EnumOp
    asn: DimValue
    asn_op: EnumOp
    country: DimValue
    country_op: EnumOp
    browser: DimValue
    browser_op: EnumOp
    os: DimValue
    os_op: EnumOp
    region: DimValue  # the serving edge region
    region_op: EnumOp
    http_version: DimValue  # "HTTP/1.1", "HTTP/2", "HTTP/3"
    http_version_op: EnumOp


_TEXT_DIMS = ("host", "path", "ua")
_ENUM_DIMS = (
    "method",
    "source_ip",
    "status",
    "protocol",
    "asn",
    "country",
    "browser",
    "os",
    "region",
    "http_version",
)
_TEXT_OPS = frozenset(("equals", "not_equals", "contains", "starts_with", "ends_with", "in", "not_in"))
_ENUM_OPS = frozenset(("equals", "not_equals", "in", "not_in"))
_FILTER_NAMES = frozenset(TrafficLogFilters.__annotations__)


def _log_list_params(filters: dict[str, Any]) -> dict[str, Any]:
    """Return the query parameters for ``list_logs`` filters.

    Checks what the API would otherwise ignore silently — an operator a
    dimension doesn't take, an operator without a value, a time without a
    timezone — because the API answers those with every entry, unfiltered.
    """
    unknown = sorted(set(filters) - _FILTER_NAMES)
    if unknown:
        raise TypeError(f"list_logs() got unexpected filter(s): {', '.join(unknown)}")
    params: dict[str, Any] = {}
    for name, value in filters.items():
        if value is None or value == "" or name.endswith("_op"):
            continue
        if isinstance(value, datetime):
            if value.tzinfo is None:
                raise ValueError(f"{name}: pass a timezone-aware datetime (the API reads RFC 3339 with an offset)")
            text = value.isoformat()
        elif isinstance(value, (str, int)):
            text = str(value)
        else:
            text = ",".join(str(v) for v in value if v is not None and v != "")
        if text:
            params[name] = text
    for dims, ops in ((_TEXT_DIMS, _TEXT_OPS), (_ENUM_DIMS, _ENUM_OPS)):
        for dim in dims:
            op = filters.get(f"{dim}_op")
            if op is None:
                continue
            if op not in ops:
                raise ValueError(f"{dim}_op={op!r}: {dim} takes {', '.join(sorted(ops))}")
            if dim not in params:
                raise ValueError(f"{dim}_op is set but {dim} is not")
            params[f"{dim}_op"] = op
    return params


class TrafficService(BaseService):
    """Sync traffic service."""

    def list_logs(
        self, page: int = 1, page_size: int = 50, **filters: Unpack[TrafficLogFilters]
    ) -> PaginatedResponse[TrafficLog]:
        """List traffic-log entries, newest first.

        Keyword filters are the API's list filters (``TrafficLogFilters``),
        e.g. ``list_logs(request_id="4f9c...")`` for the entry of one request,
        or ``list_logs(status="5xx", path="/api", path_op="starts_with")``.
        """
        params = _log_list_params(dict(filters))
        return self._client._get_page("/traffic/logs", TrafficLog, page=page, page_size=page_size, params=params)

    def get_log(self, log_uuid: str) -> dict[str, Any]:
        return self._client._get_raw(f"/traffic/logs/{path_id(log_uuid, 'log_uuid')}")

    def replay_log(self, log_uuid: str) -> dict[str, Any]:
        return self._client._post_raw(f"/traffic/logs/{path_id(log_uuid, 'log_uuid')}/replay", {})

    def analyze_log(self, log_uuid: str) -> dict[str, Any]:
        return self._client._post_raw(f"/traffic/logs/{path_id(log_uuid, 'log_uuid')}/analyze", {})

    def get_metrics(self) -> dict[str, Any]:
        return self._client._get_raw("/traffic/metrics")

    def smart_search(self, query: str) -> dict[str, Any]:
        return self._client._post_raw("/traffic/smart-search", {"query": query})


class AsyncTrafficService(AsyncBaseService):
    """Async traffic service."""

    async def list_logs(
        self, page: int = 1, page_size: int = 50, **filters: Unpack[TrafficLogFilters]
    ) -> PaginatedResponse[TrafficLog]:
        """List traffic-log entries, newest first. Filters as in ``TrafficService.list_logs``."""
        params = _log_list_params(dict(filters))
        return await self._client._get_page("/traffic/logs", TrafficLog, page=page, page_size=page_size, params=params)

    async def get_log(self, log_uuid: str) -> dict[str, Any]:
        return await self._client._get_raw(f"/traffic/logs/{path_id(log_uuid, 'log_uuid')}")

    async def replay_log(self, log_uuid: str) -> dict[str, Any]:
        return await self._client._post_raw(f"/traffic/logs/{path_id(log_uuid, 'log_uuid')}/replay", {})

    async def analyze_log(self, log_uuid: str) -> dict[str, Any]:
        return await self._client._post_raw(f"/traffic/logs/{path_id(log_uuid, 'log_uuid')}/analyze", {})

    async def get_metrics(self) -> dict[str, Any]:
        return await self._client._get_raw("/traffic/metrics")

    async def smart_search(self, query: str) -> dict[str, Any]:
        return await self._client._post_raw("/traffic/smart-search", {"query": query})
