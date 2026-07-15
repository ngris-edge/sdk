from __future__ import annotations

import pytest

from ngris._errors import (
    AuthenticationError,
    NotFoundError,
    NgrisError,
    RateLimitError,
    ServerError,
    ValidationError,
    _raise_for_status,
)


def test_401_raises_authentication_error():
    with pytest.raises(AuthenticationError) as exc_info:
        _raise_for_status(401, '{"error": "Invalid API key"}', {})
    assert exc_info.value.status_code == 401
    assert "Invalid API key" in exc_info.value.message


def test_404_raises_not_found():
    with pytest.raises(NotFoundError) as exc_info:
        _raise_for_status(404, '{"error": "Not found"}', {})
    assert exc_info.value.status_code == 404


def test_400_raises_validation_error():
    with pytest.raises(ValidationError) as exc_info:
        _raise_for_status(400, '{"error": "Bad request"}', {})
    assert exc_info.value.status_code == 400


def test_429_raises_rate_limit_with_retry_after():
    with pytest.raises(RateLimitError) as exc_info:
        _raise_for_status(429, '{"error": "Rate limit exceeded"}', {"retry-after": "30"})
    assert exc_info.value.retry_after == 30.0
    assert exc_info.value.status_code == 429


def test_500_raises_server_error():
    with pytest.raises(ServerError) as exc_info:
        _raise_for_status(500, "Internal Server Error", {})
    assert exc_info.value.status_code == 500


def test_non_json_body():
    with pytest.raises(AuthenticationError) as exc_info:
        _raise_for_status(401, "Unauthorized", {})
    assert exc_info.value.message == "Unauthorized"


def test_generic_status():
    with pytest.raises(NgrisError) as exc_info:
        _raise_for_status(418, "I'm a teapot", {})
    assert exc_info.value.status_code == 418
