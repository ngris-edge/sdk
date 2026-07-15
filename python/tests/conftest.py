from __future__ import annotations

import pytest
import respx

from ngris import AsyncNgris, Ngris


@pytest.fixture
def api_key() -> str:
    return "ngris_test_abcdef123456"


@pytest.fixture
def base_url() -> str:
    return "https://api.ngris.io"


@pytest.fixture
def client(api_key: str, base_url: str) -> Ngris:
    with Ngris(api_key=api_key, base_url=base_url, max_retries=0) as c:
        yield c


@pytest.fixture
async def async_client(api_key: str, base_url: str):
    async with AsyncNgris(api_key=api_key, base_url=base_url, max_retries=0) as c:
        yield c


@pytest.fixture
def mock_api(base_url: str):
    with respx.mock(base_url=base_url) as router:
        yield router
