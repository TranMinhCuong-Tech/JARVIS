from __future__ import annotations

import base64
import json
import os
import re
import platform
import time
from urllib.parse import quote, quote_plus
from urllib.request import Request, urlopen

from .app_launcher import open_app
from .platform_utils import open_url
from .spotify_auth import get_user_access_token

try:
    import pyautogui
except Exception:
    pyautogui = None

try:
    import pyperclip
except Exception:
    pyperclip = None


# ---------------------------------------------------------------------------
# Spotify
#
# Playing "the exact original song" AND having it actually start playing
# needs two separate things Spotify keeps apart on purpose:
#   1. Search - can be done with a simple app-only token (Client Credentials).
#   2. Command playback - the Web API's /me/player/play endpoint only accepts
#      a token that a *user* has approved (scope user-modify-playback-state).
#      An app-only token, or just opening a `spotify:track:<id>` link, can
#      only ask nicely; Spotify decides on its own whether to autoplay, which
#      is why the song was found but didn't start playing.
#
# So play_spotify now prefers a real user token: it logs the user in with
# their browser once (cached + auto-refreshed after that), then explicitly
# commands the Spotify app to start the exact track on the active device.
# ---------------------------------------------------------------------------

def play_spotify(song: str) -> str:
    """Resolve the requested song to an exact Spotify track and play it."""

    # 1) Playback-capable user token: an existing SPOTIFY_ACCESS_TOKEN env
    #    var, or one obtained (and cached) via a one-time browser login using
    #    SPOTIFY_CLIENT_ID / SPOTIFY_CLIENT_SECRET. This is the only path
    #    that can *command* Spotify to play, rather than just ask it to.
    user_token = os.getenv("SPOTIFY_ACCESS_TOKEN", "").strip() or get_user_access_token()
    if user_token:
        track_id, label = _spotify_search_track(song, user_token)
        if track_id:
            open_app("spotify")
            if _spotify_command_playback(user_token, track_id):
                return f"I am playing {label or song} on Spotify, sir."
            # The Web API play command failed (e.g. a Free account without
            # Premium, or the device still wasn't ready) - fall back to
            # opening the exact same track and pressing play for it below,
            # rather than giving up.
            if _spotify_open_and_press_play(track_id):
                return f"I am playing {label or song} on Spotify, sir."
            return f"I found {label or song} on Spotify, sir, but could not confirm playback started - press play if it hasn't."

    # 2) App-only token (search only, no playback permission) - the exact
    #    track is still resolved correctly. Since opening the track link
    #    alone isn't guaranteed to autoplay, we also press the system
    #    play/pause key right after: safe to do because the track that's
    #    loaded is already the exact one we resolved, so this only decides
    #    *whether* it plays, never *what* plays.
    app_token = _spotify_app_token()
    if app_token:
        track_id, label = _spotify_search_track(song, app_token)
        if track_id:
            open_app("spotify")
            if _spotify_open_and_press_play(track_id):
                return f"I am playing {label or song} on Spotify, sir."
            return f"I opened {label or song} on Spotify, sir, but could not confirm playback started - press play if it hasn't."

    # 3) No credentials configured at all: fall back to opening Spotify's
    #    search so the user can pick the track themselves. We deliberately no
    #    longer guess at screen coordinates here, since blind double-clicking
    #    is exactly what was causing the wrong song to play.
    open_app("spotify")
    time.sleep(3.0 if platform.system() == "Windows" else 2.0)
    open_url(f"spotify:search:{quote(song)}")
    return (
        f"I opened Spotify and searched for {song}, sir. "
    )


def _spotify_open_and_press_play(track_id: str) -> bool:
    """Open the exact resolved track, then press the system play key.

    Opening `spotify:track:<id>` only navigates/cues the track - on many
    setups (especially Free accounts) it does not start playback on its own,
    which is exactly the "found it but it didn't play" symptom. The media
    play/pause key is an OS-level signal routed to the current media app
    regardless of which window has focus, so it reliably starts the track
    that was just cued.
    """
    open_app("spotify")
    open_url(f"spotify:track:{track_id}")
    if not pyautogui:
        return False
    time.sleep(3.2 if platform.system() == "Windows" else 2.0)
    try:
        pyautogui.press("playpause")
        return True
    except Exception:
        return False


def _spotify_app_token() -> str | None:
    """Get an app-only access token via the Client Credentials flow."""
    client_id = os.getenv("SPOTIFY_CLIENT_ID", "").strip()
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET", "").strip()
    if not client_id or not client_secret:
        return None
    try:
        credentials = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("ascii")
        request = Request(
            "https://accounts.spotify.com/api/token",
            data=b"grant_type=client_credentials",
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            method="POST",
        )
        with urlopen(request, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return payload.get("access_token")
    except Exception:
        return None


def _spotify_search_track(song: str, token: str) -> tuple[str | None, str | None]:
    """Return (track_id, 'Title - Artist') for the top matching track."""
    try:
        search_url = f"https://api.spotify.com/v1/search?q={quote(song)}&type=track&limit=1"
        request = Request(search_url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
        with urlopen(request, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
        tracks = payload.get("tracks", {}).get("items", [])
        if not tracks:
            return None, None
        track = tracks[0]
        artists = ", ".join(artist.get("name", "") for artist in track.get("artists", []) if artist.get("name"))
        title = track.get("name") or song
        label = f"{title} - {artists}" if artists else title
        return track.get("id"), label
    except Exception:
        return None, None


def _spotify_command_playback(token: str, track_id: str) -> bool:
    """Explicitly start the track on an active device, with one retry.

    Right after `open_app("spotify")` the app may not have registered itself
    as an active Spotify Connect device yet, so a single failed attempt does
    not necessarily mean playback can't be started - give it a moment.
    """
    device_id = _spotify_pick_device(token)
    if device_id and _spotify_start_playback(token, track_id, device_id):
        return True

    time.sleep(2.5)
    device_id = _spotify_pick_device(token)
    return bool(device_id) and _spotify_start_playback(token, track_id, device_id)


def _spotify_pick_device(token: str) -> str | None:
    try:
        request = Request(
            "https://api.spotify.com/v1/me/player/devices",
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        )
        with urlopen(request, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
        devices = payload.get("devices", [])
        if not devices:
            return None
        active = next((device for device in devices if device.get("is_active")), None)
        return (active or devices[0]).get("id")
    except Exception:
        return None


def _spotify_start_playback(token: str, track_id: str, device_id: str | None = None) -> bool:
    try:
        url = "https://api.spotify.com/v1/me/player/play"
        if device_id:
            url += f"?device_id={quote(device_id)}"
        play_request = Request(
            url,
            data=json.dumps({"uris": [f"spotify:track:{track_id}"]}).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="PUT",
        )
        with urlopen(play_request, timeout=8):
            return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# YouTube
#
# The previous implementation grabbed the *first* "videoId" found anywhere in
# the raw search page HTML, which just as often matched a Mix, a shelf, a
# channel card, or a "people also watched" suggestion instead of the actual
# top organic result for the query. We now parse YouTube's own results JSON
# (ytInitialData) and walk only the real search-result section, picking the
# first genuine videoRenderer entry - the same video a human would click.
# ---------------------------------------------------------------------------

def play_youtube(video: str, browser: str | None = None) -> str:
    """Play the top matching YouTube video for the request."""
    video_id, title = _first_youtube_video(video)
    label = title or video
    if video_id:
        url = f"https://www.youtube.com/watch?v={video_id}&autoplay=1"
    else:
        url = f"https://www.youtube.com/results?search_query={quote_plus(video)}"

    if browser:
        open_app(browser)
        time.sleep(1.5)
        if pyautogui and pyperclip:
            pyautogui.hotkey("ctrl", "l")
            pyperclip.copy(url)
            pyautogui.hotkey("ctrl", "v")
            pyautogui.press("enter")
            if video_id:
                return f"I am playing {label} on YouTube in {browser}, sir."
            return f"I opened YouTube in {browser} to search for {video}, sir."
    open_url(url)
    if video_id:
        return f"I am playing {label} on YouTube, sir."
    return f"I opened YouTube to search for {video}, sir."


def _first_youtube_video(query: str) -> tuple[str | None, str | None]:
    """Return (video_id, title) for the top real search result, if any."""
    search_url = f"https://www.youtube.com/results?search_query={quote_plus(query)}&sp=EgIQAQ%253D%253D"
    try:
        request = Request(
            search_url,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept-Language": "en-US,en;q=0.9",
            },
        )
        with urlopen(request, timeout=8) as response:
            html = response.read().decode("utf-8", errors="ignore")
    except Exception:
        return None, None
    return _parse_youtube_first_result(html)


def _parse_youtube_first_result(html: str) -> tuple[str | None, str | None]:
    match = re.search(r"var ytInitialData\s*=\s*(\{.*?\});</script>", html, re.S)
    if not match:
        match = re.search(r'ytInitialData"\]\s*=\s*(\{.*?\});', html, re.S)
    if not match:
        return None, None

    try:
        data = json.loads(match.group(1))
    except Exception:
        return None, None

    try:
        sections = (
            data["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]
            ["sectionListRenderer"]["contents"]
        )
    except (KeyError, TypeError):
        return None, None

    for section in sections:
        items = section.get("itemSectionRenderer", {}).get("contents", [])
        for item in items:
            # Skip anything that is not a plain video result: channelRenderer,
            # shelfRenderer (Mixes/playlists), adSlotRenderer, etc. These are
            # exactly the kinds of entries that used to hijack the old regex.
            video = item.get("videoRenderer")
            if not video or not video.get("videoId"):
                continue
            runs = (video.get("title") or {}).get("runs") or []
            title = "".join(run.get("text", "") for run in runs) or None
            return video["videoId"], title

    return None, None


def send_message_flow(platform: str, receiver: str, message: str) -> str:
    """Gui tin nhan sau khi UI da xac nhan voi nguoi dung."""
    open_app(platform)
    if not pyautogui or not pyperclip:
        return "I opened the app, sir, but pyautogui and pyperclip are required to send the message automatically."
    time.sleep(2.5)
    pyautogui.hotkey("ctrl", "f")
    pyperclip.copy(receiver)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.8)
    pyautogui.press("enter")
    time.sleep(0.8)
    pyperclip.copy(message)
    pyautogui.hotkey("ctrl", "v")
    pyautogui.press("enter")
    return f"The message has been sent to {receiver} on {platform}, sir."


def find_whatsapp_contact(receiver: str) -> tuple[bool, str]:
    """Open WhatsApp and search for a contact before asking for message text."""
    open_url("https://web.whatsapp.com")
    if not pyautogui or not pyperclip:
        return False, "I opened WhatsApp Web, sir, but pyautogui and pyperclip are required to search contacts."

    time.sleep(5.0)
    pyautogui.hotkey("ctrl", "f")
    time.sleep(0.4)
    pyperclip.copy(receiver)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(1.2)

    copied = ""
    try:
        old_clipboard = pyperclip.paste()
        pyautogui.hotkey("ctrl", "a")
        pyautogui.hotkey("ctrl", "c")
        time.sleep(0.2)
        copied = pyperclip.paste()
        pyperclip.copy(old_clipboard)
    except Exception:
        copied = ""

    no_result_markers = (
        "no chats",
        "no results",
        "not found",
        "khong tim thay",
        "không tìm thấy",
    )
    if copied and any(marker in copied.lower() for marker in no_result_markers):
        return False, f"I didn't find {receiver} on your whatapp sir!"

    pyperclip.copy(receiver)
    pyautogui.hotkey("ctrl", "f")
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.8)
    pyautogui.press("enter")
    time.sleep(0.8)
    return True, f"I found {receiver} on WhatsApp, sir. What message do you want to send?"


def send_whatsapp_message(message: str) -> str:
    """Send text to the currently selected WhatsApp chat."""
    if not pyautogui or not pyperclip:
        return "pyautogui and pyperclip are required to send the message automatically, sir."
    pyperclip.copy(message)
    pyautogui.hotkey("ctrl", "v")
    pyautogui.press("enter")
    return "The message has been sent, sir."
