from __future__ import annotations

import http.server
import json
import os
import threading
import time
import urllib.parse
from base64 import b64encode
from urllib.request import Request, urlopen

from .platform_utils import app_dir, open_url

# ---------------------------------------------------------------------------
# Why this file exists
#
# An app-only token (Client Credentials flow) can *search* Spotify's catalog,
# but it can never command playback - the Web API's /me/player/play endpoint
# requires a token that a real user has approved. Without that, the previous
# approach could only open a `spotify:track:<id>` link and hope the desktop
# app decided to autoplay it, which it often didn't. This module does a
# one-time browser login (Authorization Code flow) so JARVIS gets a token
# that's actually allowed to press play, then transparently refreshes it in
# the background so the login only ever happens once.
# ---------------------------------------------------------------------------

REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPES = "user-modify-playback-state user-read-playback-state"
TOKEN_URL = "https://accounts.spotify.com/api/token"
AUTHORIZE_URL = "https://accounts.spotify.com/authorize"

_TOKEN_PATH = app_dir() / "memory" / "spotify_token.json"
_lock = threading.Lock()


def _client_credentials() -> tuple[str, str] | None:
    client_id = os.getenv("SPOTIFY_CLIENT_ID", "").strip()
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET", "").strip()
    if not client_id or not client_secret:
        return None
    return client_id, client_secret


def _basic_auth_header(client_id: str, client_secret: str) -> str:
    raw = f"{client_id}:{client_secret}".encode("utf-8")
    return "Basic " + b64encode(raw).decode("ascii")


def _load_cached_token() -> dict | None:
    try:
        if _TOKEN_PATH.exists():
            return json.loads(_TOKEN_PATH.read_text(encoding="utf-8"))
    except Exception:
        pass
    return None


def _save_token(data: dict) -> None:
    try:
        _TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        _TOKEN_PATH.write_text(json.dumps(data), encoding="utf-8")
    except Exception:
        pass


def _refresh_access_token(client_id: str, client_secret: str, refresh_token: str) -> dict | None:
    try:
        body = urllib.parse.urlencode(
            {"grant_type": "refresh_token", "refresh_token": refresh_token}
        ).encode("utf-8")
        request = Request(
            TOKEN_URL,
            data=body,
            headers={
                "Authorization": _basic_auth_header(client_id, client_secret),
                "Content-Type": "application/x-www-form-urlencoded",
            },
            method="POST",
        )
        with urlopen(request, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
        # Spotify doesn't always return a new refresh_token; keep the old one.
        payload.setdefault("refresh_token", refresh_token)
        payload["obtained_at"] = time.time()
        return payload
    except Exception:
        return None


class _CallbackHandler(http.server.BaseHTTPRequestHandler):
    result: dict = {}

    def do_GET(self) -> None:  # noqa: N802 - required name for http.server
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/callback":
            self.send_response(404)
            self.end_headers()
            return
        params = urllib.parse.parse_qs(parsed.query)
        _CallbackHandler.result["code"] = params.get("code", [None])[0]
        _CallbackHandler.result["state"] = params.get("state", [None])[0]
        _CallbackHandler.result["error"] = params.get("error", [None])[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(
            b"<html><body style='font-family:sans-serif;background:#050f16;color:#7dffb0;"
            b"text-align:center;padding-top:80px'><h2>JARVIS is connected to Spotify.</h2>"
            b"<p>You can close this tab and go back to JARVIS.</p></body></html>"
        )

    def log_message(self, *_args) -> None:  # silence default request logging
        return


def _interactive_login(client_id: str, client_secret: str, timeout: float = 90.0) -> dict | None:
    """Open the Spotify consent page once and wait for the local redirect."""
    state = str(int(time.time() * 1000))
    _CallbackHandler.result = {}

    query = urllib.parse.urlencode(
        {
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": REDIRECT_URI,
            "scope": SCOPES,
            "state": state,
        }
    )
    open_url(f"{AUTHORIZE_URL}?{query}")

    try:
        server = http.server.HTTPServer(("127.0.0.1", 8888), _CallbackHandler)
    except OSError:
        # Port already in use (e.g. a previous login attempt is still open).
        return None

    server.timeout = 1.0
    deadline = time.time() + timeout
    try:
        while time.time() < deadline and "code" not in _CallbackHandler.result:
            server.handle_request()
    finally:
        server.server_close()

    result = _CallbackHandler.result
    if not result.get("code") or result.get("state") != state:
        return None

    try:
        body = urllib.parse.urlencode(
            {
                "grant_type": "authorization_code",
                "code": result["code"],
                "redirect_uri": REDIRECT_URI,
            }
        ).encode("utf-8")
        request = Request(
            TOKEN_URL,
            data=body,
            headers={
                "Authorization": _basic_auth_header(client_id, client_secret),
                "Content-Type": "application/x-www-form-urlencoded",
            },
            method="POST",
        )
        with urlopen(request, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
        payload["obtained_at"] = time.time()
        return payload
    except Exception:
        return None


def get_user_access_token(allow_login: bool = True) -> str | None:
    """Return a playback-capable user access token.

    Uses the cached token if still valid, refreshes it silently if expired,
    and - only the very first time, and only if allow_login is True - opens a
    browser tab for the user to approve access once. Safe to call from a
    background thread; it may block briefly on network calls.
    """
    creds = _client_credentials()
    if not creds:
        return None
    client_id, client_secret = creds

    with _lock:
        token_data = _load_cached_token()

        if token_data and token_data.get("access_token"):
            expires_at = token_data.get("obtained_at", 0) + token_data.get("expires_in", 0)
            if time.time() < expires_at - 30:
                return token_data["access_token"]
            if token_data.get("refresh_token"):
                refreshed = _refresh_access_token(client_id, client_secret, token_data["refresh_token"])
                if refreshed:
                    _save_token(refreshed)
                    return refreshed.get("access_token")

        if not allow_login:
            return None

        fresh = _interactive_login(client_id, client_secret)
        if fresh and fresh.get("access_token"):
            _save_token(fresh)
            return fresh.get("access_token")

    return None
