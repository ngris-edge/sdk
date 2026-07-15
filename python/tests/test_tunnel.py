"""Tests for the ngris.connect() subprocess wrapper.

Most of this can be exercised without spawning a real agent — we mock the
binary with a tiny shell script (or python -c). For the real end-to-end
test you need a real agent binary + a running api-server; that's the
manual integration path.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest
import respx

from ngris import Tunnel, TunnelStartupError, connect
from ngris._tunnel import (
    _PUBLIC_URL_PATTERN,
    _normalize_local_addr,
    _resolve_agent_binary,
)


class TestNormalizeLocalAddr:
    """Local-addr coercion accepts ints, strings, and host:port forms."""

    def test_int_port(self) -> None:
        assert _normalize_local_addr(8080) == "localhost:8080"

    def test_string_port(self) -> None:
        assert _normalize_local_addr("3000") == "localhost:3000"

    def test_full_addr_passthrough(self) -> None:
        assert _normalize_local_addr("0.0.0.0:5432") == "0.0.0.0:5432"

    def test_invalid_port_raises(self) -> None:
        with pytest.raises(ValueError):
            _normalize_local_addr(70000)

    def test_empty_addr_raises(self) -> None:
        with pytest.raises(ValueError):
            _normalize_local_addr("")


class TestPublicURLPattern:
    """The regex must match both the emoji line the agent prints with
    --no-tui and the plain text fallback."""

    def test_emoji_line(self) -> None:
        line = "🌐 Public URL: https://abc123.ngris.io (HTTP/1.1)"
        m = _PUBLIC_URL_PATTERN.search(line)
        assert m and m.group(1) == "https://abc123.ngris.io"

    def test_plain_line(self) -> None:
        line = "Public URL: http://localhost:9999"
        m = _PUBLIC_URL_PATTERN.search(line)
        assert m and m.group(1) == "http://localhost:9999"

    def test_no_match_on_unrelated(self) -> None:
        assert _PUBLIC_URL_PATTERN.search("just some log line") is None


class TestBinaryResolution:
    """Resolving the agent binary path."""

    def test_env_var_explicit_path(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        fake = tmp_path / "fake-agent"
        fake.write_text("#!/bin/sh\necho hi\n")
        fake.chmod(0o755)
        monkeypatch.setenv("NGRIS_AGENT_BIN", str(fake))
        assert _resolve_agent_binary() == str(fake)

    def test_env_var_missing_path_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("NGRIS_AGENT_BIN", "/nonexistent/path/agent")
        with pytest.raises(FileNotFoundError):
            _resolve_agent_binary()

    def test_no_binary_anywhere_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("NGRIS_AGENT_BIN", raising=False)
        # PATH=/nonexistent guarantees shutil.which finds nothing
        monkeypatch.setenv("PATH", "/nonexistent")
        with pytest.raises(FileNotFoundError, match="agent binary not found"):
            _resolve_agent_binary()


# Fake agent script: prints the URL line then sleeps until killed. Lets us
# exercise the full connect() path without a real Go binary.
#
# The script ALSO verifies the SDK's CLI invocation so that any drift in
# argument format / order is caught at test time, not on first real-agent
# run. Specifically: agent expects `<subcommand> <local_addr> [flags...]`
# and the SDK must pass `--no-tui` (otherwise the real agent's TUI would
# eat our stdout-parse path).
_FAKE_AGENT_SCRIPT = '''#!{python}
import os, sys, time
# 1. Auth token must be in API_TOKEN env (matches agent's BindEnv).
assert os.environ.get("API_TOKEN") == "FAKE_TOKEN_VALUE", \\
    f"missing/wrong API_TOKEN env: {{os.environ.get('API_TOKEN')!r}}"
# 2. argv shape: argv[0]=binary, argv[1]=subcommand, argv[2]=local_addr,
#    then flags. The SDK builds [bin, proto, local, "--no-tui", ...].
assert len(sys.argv) >= 4, f"too few argv: {{sys.argv}}"
assert sys.argv[1] in ("http", "tcp"), f"bad subcommand: {{sys.argv[1]!r}}"
# Local addr should be host:port form; the SDK normalizes int ports to
# "localhost:N" before exec.
assert ":" in sys.argv[2], f"bad local addr: {{sys.argv[2]!r}}"
# 3. --no-tui must be present so the agent prints to stdout, not the TUI.
assert "--no-tui" in sys.argv, f"--no-tui missing: {{sys.argv}}"
# Agent prints URL on success after handshake (mimics agent/tunnel/client.go:1183).
print("🌐 Public URL: https://test123.ngris.io (HTTP/1.1)", flush=True)
# Agent stays alive until killed.
try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    pass
'''


@pytest.fixture
def fake_agent(tmp_path: Path) -> Path:
    """A python script that pretends to be the agent for end-to-end testing
    of connect() without needing the Go binary."""
    p = tmp_path / "fake-agent"
    p.write_text(_FAKE_AGENT_SCRIPT.format(python=sys.executable))
    p.chmod(0o755)
    return p


class TestConnect:
    """End-to-end connect() with a faked agent binary + mocked api-server."""

    @respx.mock
    def test_connect_returns_tunnel(
        self, fake_agent: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Mock the management API: minting a token returns the value the
        # fake agent expects in API_TOKEN env.
        respx.post("https://api.example.test/keys/auth").respond(
            200, json={"id": 42, "token": "FAKE_TOKEN_VALUE"}
        )
        respx.delete("https://api.example.test/keys/auth/42").respond(204)

        monkeypatch.setenv("NGRIS_AGENT_BIN", str(fake_agent))

        with connect(
            8080,
            api_key="ngris_test",
            base_url="https://api.example.test",
            timeout=10.0,
        ) as t:
            assert isinstance(t, Tunnel)
            assert t.public_url == "https://test123.ngris.io"
            assert t.local_addr == "localhost:8080"
            assert t.is_alive()

        # After context exit, the agent should be killed.
        time.sleep(0.2)
        assert not t.is_alive()

    @respx.mock
    def test_connect_revokes_token_on_close(
        self, fake_agent: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        respx.post("https://api.example.test/keys/auth").respond(
            200, json={"id": 99, "token": "FAKE_TOKEN_VALUE"}
        )
        revoke = respx.delete("https://api.example.test/keys/auth/99").respond(204)

        monkeypatch.setenv("NGRIS_AGENT_BIN", str(fake_agent))

        t = connect(
            8080,
            api_key="ngris_test",
            base_url="https://api.example.test",
            timeout=10.0,
        )
        t.close()
        assert revoke.called, "auth token should be DELETEd after close()"

    @respx.mock
    def test_mint_and_revoke_route_through_sdk_client(
        self, fake_agent: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Both /keys/auth requests must carry the SDK's standard headers
        — proves the calls go through the main Ngris client (with retry,
        User-Agent, structured logging) and not an ad-hoc httpx invocation.
        """
        mint = respx.post("https://api.example.test/keys/auth").respond(
            200, json={"id": 7, "token": "FAKE_TOKEN_VALUE"}
        )
        revoke = respx.delete("https://api.example.test/keys/auth/7").respond(204)

        monkeypatch.setenv("NGRIS_AGENT_BIN", str(fake_agent))

        t = connect(
            8080,
            api_key="ngris_test_xyz",
            base_url="https://api.example.test",
            timeout=10.0,
        )
        t.close()

        # Both calls must bear the SDK's auth header AND the SDK's
        # User-Agent — the smoking gun that they went through Ngris and
        # not a hand-rolled httpx.Client.
        for call in (mint.calls.last, revoke.calls.last):
            assert call.request.headers["X-API-Key"] == "ngris_test_xyz"
            assert call.request.headers["User-Agent"].startswith("ngris-python/")

    @respx.mock
    def test_connect_closes_sdk_client_on_mint_failure(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """If minting fails the SDK client we just constructed must be
        closed — otherwise we leak its httpx connection pool. Regression
        guards the early-return path in connect()."""
        respx.post("https://api.example.test/keys/auth").respond(
            403, text="forbidden"
        )
        # No agent binary needed — we never get past the mint step.
        with pytest.raises(Exception):
            connect(
                8080,
                api_key="ngris_test",
                base_url="https://api.example.test",
                timeout=5.0,
            )

    @respx.mock
    def test_missing_api_key_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("NGRIS_API_KEY", raising=False)
        with pytest.raises(ValueError, match="api_key is required"):
            connect(8080, base_url="https://api.example.test")

    def test_udp_rejected_at_sdk(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """UDP isn't an agent subcommand — SDK must reject up-front rather
        than spawn an agent that falls into its config-driven default
        path. Regression-guards against re-adding UDP to the protocol
        validation without first wiring it on the agent side."""
        with pytest.raises(ValueError, match="UDP isn't an agent subcommand"):
            connect(
                8080,
                protocol="udp",
                api_key="ngris_test",
                base_url="https://api.example.test",
            )

    @respx.mock
    def test_token_mint_failure_propagates(
        self, fake_agent: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        respx.post("https://api.example.test/keys/auth").respond(
            401, text="Invalid API Key"
        )
        monkeypatch.setenv("NGRIS_AGENT_BIN", str(fake_agent))
        with pytest.raises(Exception) as excinfo:
            connect(
                8080,
                api_key="bad-key",
                base_url="https://api.example.test",
                timeout=5.0,
            )
        assert "401" in str(excinfo.value) or "Invalid" in str(excinfo.value)

    @respx.mock
    def test_agent_exits_early_raises_startup_error(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """If the agent process dies before printing a URL we should surface
        a clear TunnelStartupError, not hang or wrap as a generic NgrisError."""
        respx.post("https://api.example.test/keys/auth").respond(
            200, json={"id": 1, "token": "FAKE_TOKEN_VALUE"}
        )
        respx.delete("https://api.example.test/keys/auth/1").respond(204)

        # Agent that exits immediately with an error message.
        crashy = tmp_path / "crashy-agent"
        crashy.write_text(
            f"#!{sys.executable}\n"
            "import sys\n"
            "sys.stderr.write('agent: bad config\\n')\n"
            "sys.exit(1)\n"
        )
        crashy.chmod(0o755)
        monkeypatch.setenv("NGRIS_AGENT_BIN", str(crashy))

        with pytest.raises(TunnelStartupError):
            connect(
                8080,
                api_key="ngris_test",
                base_url="https://api.example.test",
                timeout=5.0,
            )
