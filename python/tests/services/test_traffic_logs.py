"""traffic.list_logs: request_id on every entry, and the API's list filters.

Pins the exact query the SDK sends (the API's own parameter names and
operators), that calls without filters send what they always did, and that
mistakes the API would silently answer with every entry, unfiltered, are
refused before any request is made.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import httpx
import pytest
import respx

from ngris import AsyncNgris, Ngris
from ngris.models import TrafficLog

BASE = "https://api.example.test"
LOGS = f"{BASE}/traffic/logs"
RID = "4f9c2b7e1d0a8c3b6e5f7a9d2c1b0e8f"
EP = "019bb1e4-e785-77d2-9966-c3cff31d0a0e"
PAGE = {
    "items": [
        {"uuid": "019ba303-954b-796c-bf40-f33a26697f74", "request_id": RID, "method": "GET", "status_code": 200},
        {"uuid": "019ba303-954b-796c-bf40-f33a26697f75", "source_ip": "192.0.2.10"},
    ],
    "total": 2,
    "page": 1,
    "page_size": 50,
}


@pytest.fixture
def client() -> Ngris:
    return Ngris(api_key="ngris_test", base_url=BASE, max_retries=0)


def _query(route: respx.Route) -> dict[str, str]:
    return dict(route.calls.last.request.url.params)


@respx.mock
def test_unfiltered_call_is_unchanged(client: Ngris) -> None:
    route = respx.get(LOGS).respond(200, json=PAGE)
    page = client.traffic.list_logs()
    assert _query(route) == {"page": "1", "page_size": "50"}
    client.traffic.list_logs(2, 100)  # positional page / page_size still work
    assert _query(route) == {"page": "2", "page_size": "100"}
    # request_id is on the model; an entry without one has None.
    assert isinstance(page.items[0], TrafficLog)
    assert page.items[0].request_id == RID
    assert page.items[1].request_id is None


@respx.mock
def test_request_id_filter(client: Ngris) -> None:
    route = respx.get(LOGS).respond(200, json={**PAGE, "items": PAGE["items"][:1], "total": 1})
    page = client.traffic.list_logs(request_id=RID)
    assert _query(route) == {"page": "1", "page_size": "50", "request_id": RID}
    assert [log.request_id for log in page.items] == [RID]


@respx.mock
def test_filters_use_the_api_names_and_operators(client: Ngris) -> None:
    route = respx.get(LOGS).respond(200, json=PAGE)
    since = datetime(2026, 10, 19, 8, 0, tzinfo=timezone.utc)
    until = datetime(2026, 10, 19, 11, 0, tzinfo=timezone(timedelta(hours=3)))
    client.traffic.list_logs(
        page_size=200,
        endpoint_uuid=EP,
        since=since,
        until=until,
        status=["404", "5xx"],
        method="POST",
        path="/api/",
        path_op="starts_with",
        country=["DE", "FR"],
        country_op="not_in",
        region="eu-north-1",
        http_version="HTTP/2",
        http_version_op="not_equals",
        firewall_action="blocked",
        search=None,  # None means "no filter"
    )
    assert _query(route) == {
        "page": "1",
        "page_size": "200",
        "endpoint_uuid": EP,
        "since": "2026-10-19T08:00:00+00:00",
        "until": "2026-10-19T11:00:00+03:00",
        "status": "404,5xx",
        "method": "POST",
        "path": "/api/",
        "path_op": "starts_with",
        "country": "DE,FR",
        "country_op": "not_in",
        "region": "eu-north-1",
        "http_version": "HTTP/2",
        "http_version_op": "not_equals",
        "firewall_action": "blocked",
    }


@respx.mock
def test_status_as_an_int_and_cursor_filters(client: Ngris) -> None:
    route = respx.get(LOGS).respond(200, json=PAGE)
    client.traffic.list_logs(status=500, since_uuid=EP, time_range="24h", rate_limit_rule_uuid=EP)
    assert _query(route) == {
        "page": "1",
        "page_size": "50",
        "status": "500",
        "since_uuid": EP,
        "time_range": "24h",
        "rate_limit_rule_uuid": EP,
    }


@pytest.mark.parametrize(
    "filters, error",
    [
        ({"requestid": RID}, TypeError),  # a misspelt filter
        ({"status": "500", "status_op": "contains"}, ValueError),  # an op status doesn't take
        ({"host_op": "contains"}, ValueError),  # an op without its value
        ({"since": datetime(2026, 10, 19, 8, 0)}, ValueError),  # no timezone
    ],
)
@respx.mock
def test_mistakes_the_api_would_ignore_are_refused(client: Ngris, filters: dict, error: type) -> None:
    route = respx.get(LOGS).respond(200, json=PAGE)
    with pytest.raises(error):
        client.traffic.list_logs(**filters)
    assert not route.called


@respx.mock
async def test_async_list_logs_filters() -> None:
    route = respx.get(LOGS).respond(200, json=PAGE)
    async with AsyncNgris(api_key="ngris_test", base_url=BASE, max_retries=0) as aclient:
        page = await aclient.traffic.list_logs(request_id=RID, host=["a.test", "b.test"], host_op="in")
        assert page.items[0].request_id == RID
        assert _query(route) == {
            "page": "1",
            "page_size": "50",
            "request_id": RID,
            "host": "a.test,b.test",
            "host_op": "in",
        }
        await aclient.traffic.list_logs()
        assert _query(route) == {"page": "1", "page_size": "50"}
        with pytest.raises(ValueError):
            await aclient.traffic.list_logs(region="x", region_op="starts_with")


def test_query_is_url_encoded(client: Ngris) -> None:
    with respx.mock:
        route = respx.get(LOGS).respond(200, json=PAGE)
        client.traffic.list_logs(http_version="HTTP/1.1", path="/a b&c")
        raw = str(route.calls.last.request.url)
    assert "http_version=HTTP%2F1.1" in raw
    assert httpx.URL(raw).params["path"] == "/a b&c"


# One list item exactly as api-server's GET /traffic/logs returns it (every
# field of its list projection, as a non-admin caller gets it).
API_LIST_ITEM = {
    "id": 331,
    "uuid": "019ba303-954b-796c-bf40-f33a26697f74",
    "method": "POST",
    "path": "/checkout",
    "host": "myapp.ngris.io",
    "tunnel_type": "http",
    "public_url": "https://myapp.ngris.io",
    "region": "eu-north-1",
    "http_version": "HTTP/2",
    "request_id": RID,
    "source_ip": "198.51.100.7",
    "status_code": 500,
    "origin_status": 500,
    "latency_ms": 1243,
    "duration_ms": 1247,
    "edge_ms": 2,
    "origin_ttfb_ms": 1243,
    "transfer_ms": 2,
    "bytes_in": 312,
    "bytes_out": 22,
    "firewall_action": "no_match",
    "rate_limit_action": "allowed",
    "is_replay": False,
    "geo_info": {"country": "US", "asn": "AS64500"},
    "spam_score": 4,
    "ip_health": "clean",
    "created_at": "2026-10-19T08:00:00Z",
}
TCP_ITEM = {
    "id": 332,
    "uuid": "019ba303-954b-796c-bf40-f33a26697f75",
    "tunnel_type": "tcp",
    "public_url": "tcp://myapp.ngris.io:17032",
    "connection_id": "c-9f3a4e1b2d",
    "source_ip": "192.0.2.10",
    "bytes_in": 48213,
    "bytes_out": 99120,
    "duration_ms": 60321,
    "is_replay": False,
    "created_at": "2026-10-19T08:00:01Z",
}


@respx.mock
def test_every_list_field_is_typed(client: Ngris) -> None:
    respx.get(LOGS).respond(200, json={"items": [API_LIST_ITEM, TCP_ITEM], "total": 2, "page": 1, "page_size": 50})
    http_row, tcp_row = client.traffic.list_logs().items
    dumped = http_row.model_dump(exclude_none=True)
    for name, value in API_LIST_ITEM.items():
        if name == "created_at":
            assert http_row.created_at == datetime(2026, 10, 19, 8, 0, tzinfo=timezone.utc)
            continue
        assert dumped[name] == value, name
    assert tcp_row.connection_id == "c-9f3a4e1b2d"
    assert tcp_row.tunnel_type == "tcp"
    assert tcp_row.host is None and tcp_row.request_id is None and tcp_row.http_version is None
