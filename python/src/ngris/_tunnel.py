"""Subprocess wrapper for the Ngris agent binary.

Provides a Python-native `ngris.connect(8080)` that spawns the agent in the
background and returns a Tunnel handle exposing `.public_url`. Mirrors the
ngrok-Python ergonomic — the SDK manages the agent lifecycle, the user's
code never has to think about handshakes or auth tokens.

How it works:
  1. Mint a per-tunnel auth_token via POST /keys/auth (using the user's
     NGRIS_API_KEY).
  2. Resolve the agent binary path (env var → PATH → bundled).
  3. Spawn it with `--no-tui` and the right CLI args, passing the auth
     token via API_TOKEN env var.
  4. Tail stdout for the line `🌐 Public URL: <url>` (or its plain-text
     fallback) — block until it appears or timeout fires.
  5. Return a Tunnel object. `.close()` SIGTERMs the subprocess and
     revokes the auth_token so it doesn't pile up in the DB.
"""

from __future__ import annotations

import atexit
import os
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from typing import Optional

from ngris._config import NgrisConfig
from ngris._errors import NgrisError
from ngris._sync_client import Ngris


# Binary names we search for, in order. `ngris-agent` is the planned future
# rename; `easytunnel-agent` is the current Go build artifact. Either works.
_AGENT_BINARY_CANDIDATES = ("ngris-agent", "easytunnel-agent")

# Override path via env var: NGRIS_AGENT_BIN=/full/path/to/agent
_AGENT_BIN_ENV = "NGRIS_AGENT_BIN"

# Regex matches both the emoji-decorated "🌐 Public URL: https://..." line
# the agent prints when --no-tui is set (see agent/tunnel/client.go:1183
# `fmt.Printf("🌐 Public URL: %s (%s)\n", publicEndpoint, httpVersion)`),
# and a plain "Public URL: https://..." fallback. The first capturing
# group is the bare URL — we stop at whitespace only because the agent
# always prints " (HTTP/1.1)" after the URL with a leading space.
_PUBLIC_URL_PATTERN = re.compile(r"Public URL:\s*(https?://\S+)")

# Default time we'll wait for the agent to print a public URL before giving
# up. Covers DNS resolution + TLS handshake + endpoint provisioning on a
# slow link. Override per-call via `connect(timeout=...)`.
_DEFAULT_CONNECT_TIMEOUT = 30.0


@dataclass
class _AuthTokenHandle:
    """Tracks a server-side auth_token so the Tunnel can revoke it on close."""
    id: int
    raw: str


class TunnelStartupError(NgrisError):
    """Agent process exited before establishing a tunnel, or the URL never
    appeared in its output. Carries the captured stderr so the user can
    diagnose (wrong server, bad token, port in use, etc).
    """


def _resolve_agent_binary() -> str:
    """Find the agent binary.

    Order of resolution:
      1. NGRIS_AGENT_BIN env var (explicit path)
      2. `ngris-agent` on PATH
      3. `easytunnel-agent` on PATH
      4. Bundled `<package>/bin/<binary>` (placeholder for future wheels)

    Raises FileNotFoundError with an install hint if none found.
    """
    explicit = os.environ.get(_AGENT_BIN_ENV)
    if explicit:
        if os.path.isfile(explicit) and os.access(explicit, os.X_OK):
            return explicit
        raise FileNotFoundError(
            f"{_AGENT_BIN_ENV}={explicit!r} is not executable"
        )

    for candidate in _AGENT_BINARY_CANDIDATES:
        found = shutil.which(candidate)
        if found:
            return found

    # Future: bundled binary path. Wheels for linux/macos/windows × amd64/arm64
    # would land here. For now this just raises with install instructions.
    raise FileNotFoundError(
        "ngris agent binary not found.\n"
        "Install via:\n"
        "  curl -fsSL https://ngris.io/install.sh | sh   # installs to /usr/local/bin\n"
        "Or set NGRIS_AGENT_BIN=/path/to/agent and re-run."
    )


class Tunnel:
    """Live tunnel handle. Wraps a running agent subprocess.

    Use as a context manager (auto-close on exit) or call `.close()` manually.
    Process is also killed automatically at interpreter shutdown via atexit.
    """

    def __init__(
        self,
        proc: subprocess.Popen,
        public_url: str,
        local_addr: str,
        token: Optional[_AuthTokenHandle] = None,
        client: Optional[Ngris] = None,
    ) -> None:
        self._proc = proc
        self.public_url = public_url
        self.local_addr = local_addr
        self._token = token
        # The Ngris client used to mint the token — we keep it around so
        # close() can revoke through the same authenticated client (gets
        # SDK retry, logging, request_id propagation for free instead of
        # an ad-hoc httpx call).
        self._client = client
        self._closed = False
        # Register cleanup for the case where the user forgets to call close()
        # AND doesn't use the context manager. Without this the agent keeps
        # running after the Python process exits (leaks).
        atexit.register(self._atexit_cleanup)

    @property
    def pid(self) -> int:
        return self._proc.pid

    def is_alive(self) -> bool:
        return self._proc.poll() is None

    def close(self, timeout: float = 5.0) -> None:
        """Stop the agent and revoke its auth token. Idempotent."""
        if self._closed:
            return
        self._closed = True
        try:
            atexit.unregister(self._atexit_cleanup)
        except Exception:
            pass
        # Step 1: graceful SIGTERM
        if self._proc.poll() is None:
            try:
                self._proc.terminate()
                self._proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                # Step 2: force kill if it ignored SIGTERM
                self._proc.kill()
                try:
                    self._proc.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    pass
            except Exception:
                pass
        # Step 3: revoke the auth token via the management API. Best-effort
        # — server-side cleanup happens on token expiry anyway, but revoking
        # explicitly avoids piling up tokens on rapid connect/close cycles.
        if self._token is not None and self._client is not None:
            try:
                self._client.api_keys.delete_auth_token(self._token.id)
            except Exception:
                pass
        # Whether or not the revoke worked, close the client we own so we
        # don't leak the underlying httpx connection pool.
        if self._client is not None:
            try:
                self._client.close()
            except Exception:
                pass

    def _atexit_cleanup(self) -> None:
        # Don't block the interpreter shutdown — short timeout, no token
        # revoke (network may be torn down already).
        if self._closed or self._proc.poll() is not None:
            return
        try:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                self._proc.kill()
        except Exception:
            pass

    def __enter__(self) -> "Tunnel":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def __repr__(self) -> str:
        state = "alive" if self.is_alive() else "closed"
        return f"<Tunnel {self.public_url} -> {self.local_addr} ({state})>"


def _normalize_local_addr(addr: object) -> str:
    """Accept int port, "5432", "localhost:5432", "0.0.0.0:8080", etc."""
    if isinstance(addr, int):
        if not (1 <= addr <= 65535):
            raise ValueError(f"port out of range: {addr}")
        return f"localhost:{addr}"
    s = str(addr).strip()
    if not s:
        raise ValueError("local address required")
    # Bare port string?
    if ":" not in s:
        try:
            p = int(s)
            if 1 <= p <= 65535:
                return f"localhost:{p}"
        except ValueError:
            pass
    return s


def _mint_auth_token(client: Ngris, description: str) -> _AuthTokenHandle:
    """POST /keys/auth via the management client.

    Routing through ``client.api_keys.create_auth_token`` (instead of an
    ad-hoc ``httpx`` call) means the mint request inherits the SDK's
    retry policy, structured logging, error mapping, and User-Agent —
    one code path for every server interaction.
    """
    data = client.api_keys.create_auth_token(description=description)
    tok = data.get("token")
    tid = data.get("id")
    if not tok or tid is None:
        raise NgrisError(f"unexpected /keys/auth response: {data!r}")
    return _AuthTokenHandle(id=int(tid), raw=str(tok))


def _wait_for_public_url(
    proc: subprocess.Popen,
    timeout: float,
) -> tuple[str, list[str]]:
    """Read agent stdout line-by-line until we see a Public URL line, the
    process exits, or `timeout` elapses. Returns (url, stderr_lines).

    Spawns a stderr-drain thread so the agent doesn't block on a full stderr
    pipe while we're reading stdout.
    """
    stderr_lines: list[str] = []
    stderr_lock = threading.Lock()

    def _drain_stderr() -> None:
        if proc.stderr is None:
            return
        for line in iter(proc.stderr.readline, ""):
            if not line:
                break
            with stderr_lock:
                stderr_lines.append(line.rstrip("\n"))

    drain = threading.Thread(target=_drain_stderr, daemon=True)
    drain.start()

    deadline = time.monotonic() + timeout
    public_url: Optional[str] = None

    if proc.stdout is None:
        # Shouldn't happen given our Popen call, but be defensive.
        with stderr_lock:
            captured = list(stderr_lines)
        raise TunnelStartupError("agent stdout was not piped", headers={})

    # We'd love to use a non-blocking readline with a timeout, but stdlib
    # doesn't give us one without going through select on the fd. Inline
    # the select.poll() loop instead.
    import selectors

    sel = selectors.DefaultSelector()
    sel.register(proc.stdout, selectors.EVENT_READ)

    while True:
        if proc.poll() is not None:
            # Process exited before printing the URL. Surface stderr so the
            # caller sees the agent's error message.
            time.sleep(0.05)  # let the stderr drain catch up
            with stderr_lock:
                captured = list(stderr_lines)
            raise TunnelStartupError(
                "agent exited before establishing tunnel"
                + (f": {captured[-1]}" if captured else ""),
            )
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            with stderr_lock:
                captured = list(stderr_lines)
            raise TunnelStartupError(
                f"timeout after {timeout}s waiting for agent to print Public URL"
                + (f": {captured[-1]}" if captured else ""),
            )
        events = sel.select(timeout=min(remaining, 0.5))
        if not events:
            continue
        line = proc.stdout.readline()
        if not line:
            continue
        m = _PUBLIC_URL_PATTERN.search(line)
        if m:
            public_url = m.group(1)
            break

    with stderr_lock:
        captured = list(stderr_lines)
    return public_url, captured  # type: ignore[return-value]


def connect(
    addr: object = 80,
    *,
    protocol: str = "http",
    hostname: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    server: Optional[str] = None,
    timeout: float = _DEFAULT_CONNECT_TIMEOUT,
    agent_bin: Optional[str] = None,
    extra_args: Optional[list[str]] = None,
) -> Tunnel:
    """Open a tunnel to a local service. Returns a Tunnel handle whose
    `.public_url` points at the live tunnel.

    Args:
      addr:      Local target. Int port (8080), bare port string ("8080"),
                 host:port ("localhost:5432"), or "0.0.0.0:8080".
      protocol:  "http", "tcp", or "udp". Default "http".
      hostname:  Optional fixed public hostname (e.g. "myapp.example.com").
                 Requires a registered domain in the user's account. Default
                 is to request an ephemeral subdomain.
      api_key:   Ngris API key. Falls back to NGRIS_API_KEY env var.
      base_url:  Management API base URL. Falls back to NGRIS_BASE_URL or
                 https://api.ngris.io.
      server:    Tunnel-server address (host:port). Usually inferred from
                 the agent's config; override for self-hosted deployments.
      timeout:   Seconds to wait for the agent to come up. Default 30s.
      agent_bin: Override the agent binary path (alternative to
                 NGRIS_AGENT_BIN env var).
      extra_args: Extra CLI flags to pass through to the agent.

    Example:
      with ngris.connect(8080) as t:
          print(t.public_url)   # https://abc123.ngris.io
    """
    # Resolve config like the management client does — env-var fallbacks +
    # explicit args. We don't construct a full NgrisConfig because we only
    # need a couple of values, and we want to skip the api_key-required
    # check when the user has set NGRIS_API_KEY in env.
    cfg = NgrisConfig(api_key=api_key or "", base_url=base_url or "")
    if not cfg.api_key:
        raise ValueError(
            "api_key is required. Pass api_key=... or set NGRIS_API_KEY env var."
        )

    proto = protocol.lower()
    # Agent's subcommand dispatch (agent/main.go) recognizes "http", "tcp",
    # "webfm", "auth", "version". UDP is NOT a top-level subcommand even
    # though the rest of the platform supports UDP tunnels — so the SDK
    # must reject it here rather than silently spawn an agent that falls
    # through to its config-driven default path.
    if proto not in ("http", "tcp"):
        raise ValueError(
            f"unsupported protocol: {protocol!r} "
            f"(expected 'http' or 'tcp'; UDP isn't an agent subcommand)"
        )

    local = _normalize_local_addr(addr)
    binary = agent_bin or _resolve_agent_binary()

    # Build a management client and own its lifecycle. We attach it to the
    # returned Tunnel so close() can revoke the auth token through the
    # same authenticated path. If anything below this line raises, the
    # except branch closes the client so we don't leak its connection pool.
    sdk_client = Ngris(api_key=cfg.api_key, base_url=cfg.base_url)

    # Mint a per-tunnel auth_token. Description ties it back to the SDK so
    # admins can see "where did this token come from" in the dashboard.
    description = f"ngris-python sdk ({proto} {local})"
    try:
        token = _mint_auth_token(sdk_client, description=description)
    except Exception:
        sdk_client.close()
        raise

    # Build CLI invocation. The agent's subcommand is the protocol. `--no-tui`
    # is essential — the TUI captures the terminal and never prints the URL
    # in the form we can parse.
    cmd: list[str] = [binary, proto, local, "--no-tui"]
    if hostname:
        cmd += ["--url", hostname]
    if server:
        cmd += ["--server", server]
    if extra_args:
        cmd += list(extra_args)

    env = os.environ.copy()
    env["API_TOKEN"] = token.raw

    # Per-platform flags to detach the agent from our terminal/process group.
    # On POSIX: os.setsid puts the agent in its own session so SIGINT/SIGTERM
    # to the parent doesn't cascade — close() controls it explicitly.
    # On Windows: CREATE_NEW_PROCESS_GROUP achieves the same isolation; the
    # constant only exists on Windows builds of the stdlib, so getattr() is
    # how we reference it without a NameError on POSIX.
    popen_kwargs: dict = {}
    if sys.platform == "win32":
        popen_kwargs["creationflags"] = getattr(
            subprocess, "CREATE_NEW_PROCESS_GROUP", 0
        )
    elif hasattr(os, "setsid"):
        popen_kwargs["preexec_fn"] = os.setsid

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,
            bufsize=1,  # line-buffered so readline() doesn't block on chunks
            **popen_kwargs,
        )
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"failed to spawn agent at {binary!r}: {e}"
        ) from e

    try:
        public_url, _ = _wait_for_public_url(proc, timeout=timeout)
    except Exception:
        # Cleanup on startup failure: graceful SIGTERM first (let agent
        # close its tunnel-server connection cleanly), SIGKILL only if it
        # ignores. Mirrors the Tunnel.close() escalation so behavior is
        # consistent regardless of whether failure happened before or
        # after we got a Tunnel handle.
        try:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=2.0)
                except subprocess.TimeoutExpired:
                    proc.kill()
        except Exception:
            pass
        # Revoke the token we just minted (best-effort: the api-server may
        # already be the reason connect() failed) and close the SDK client
        # we own. Routing through the SDK client means this revoke gets
        # the same retry/logging treatment as any other DELETE.
        try:
            sdk_client.api_keys.delete_auth_token(token.id)
        except Exception:
            pass
        try:
            sdk_client.close()
        except Exception:
            pass
        raise

    return Tunnel(
        proc=proc,
        public_url=public_url,
        local_addr=local,
        token=token,
        client=sdk_client,
    )


def disconnect(tunnel: Tunnel) -> None:
    """Convenience function — equivalent to tunnel.close()."""
    tunnel.close()


def kill_all() -> None:
    """No-op placeholder. Reserved for future "kill every running agent
    started by this Python process" functionality (would require tracking
    active Tunnel instances in a weakref set). Provided so the API surface
    matches user expectations from ngrok-python.
    """
    # Intentional: doc reservation only. See atexit hooks on Tunnel for the
    # actual auto-cleanup behavior.
    pass
