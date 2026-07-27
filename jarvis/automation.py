from __future__ import annotations

import json
import os
import re
import platform
import time
from urllib.parse import quote, quote_plus
from urllib.request import Request, urlopen

from .app_launcher import open_app
from .platform_utils import open_url

try:
    import pyautogui
except Exception:
    pyautogui = None

try:
    import pyperclip
except Exception:
    pyperclip = None


def play_spotify(song: str) -> str:
    """Mo Spotify, tim bai hat va co gang phat ket qua dau tien."""
    query = quote_plus(song)
    if _spotify_web_api_play(song):
        return f"I am playing {song} on Spotify, sir."

    open_app("spotify")
    if pyautogui and pyperclip:
        time.sleep(3.5 if platform.system() == "Windows" else 2.5)
        try:
            _spotify_search_and_play(song)
            return f"I am searching for and playing {song} on Spotify, sir."
        except Exception as exc:
            return f"I found {song} on Spotify, sir, but could not press play automatically: {exc}"
    open_url(f"https://open.spotify.com/search/{query}")
    return f"I opened Spotify search for {song}, sir. Install pyautogui and pyperclip to autoplay it."


def _spotify_web_api_play(song: str) -> bool:
    token = os.getenv("SPOTIFY_ACCESS_TOKEN", "").strip()
    if not token:
        return False

    try:
        search_url = f"https://api.spotify.com/v1/search?q={quote(song)}&type=track&limit=1"
        request = Request(search_url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
        with urlopen(request, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
        tracks = payload.get("tracks", {}).get("items", [])
        if not tracks:
            return False

        track_uri = tracks[0].get("uri")
        if not track_uri:
            return False

        play_request = Request(
            "https://api.spotify.com/v1/me/player/play",
            data=json.dumps({"uris": [track_uri]}).encode("utf-8"),
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


def _spotify_search_and_play(song: str) -> None:
    """Search first, then activate the first Spotify result."""
    assert pyautogui is not None
    assert pyperclip is not None

    old_failsafe = getattr(pyautogui, "FAILSAFE", True)
    pyautogui.FAILSAFE = False
    try:
        open_url(f"spotify:search:{quote(song)}")
        time.sleep(2.4)
        _spotify_play_first_search_result()
    finally:
        pyautogui.FAILSAFE = old_failsafe


def _spotify_play_first_search_result() -> None:
    assert pyautogui is not None

    # The URI opens the requested search page first. Double-clicking the top
    # result is closer to how Spotify Desktop reliably starts a searched song.
    pyautogui.press("esc")
    time.sleep(0.35)
    if _spotify_double_click_top_result():
        return

    # Keyboard fallback for layouts where the active window position cannot be
    # read. Space is still avoided because it can toggle the previous track.
    pyautogui.press("home")
    time.sleep(0.2)
    for _ in range(2):
        pyautogui.press("tab")
        time.sleep(0.18)
    pyautogui.press("down")
    time.sleep(0.18)
    pyautogui.press("enter")
    time.sleep(0.9)
    pyautogui.press("enter")


def _spotify_double_click_top_result() -> bool:
    assert pyautogui is not None

    try:
        window = pyautogui.getActiveWindow()
    except Exception:
        window = None

    try:
        if window and window.width > 300 and window.height > 260:
            x = window.left + int(window.width * 0.42)
            y = window.top + int(window.height * 0.38)
        else:
            screen_w, screen_h = pyautogui.size()
            x = int(screen_w * 0.42)
            y = int(screen_h * 0.38)
        pyautogui.doubleClick(x, y, interval=0.08)
        time.sleep(0.8)
        return True
    except Exception:
        return False


def play_youtube(video: str, browser: str | None = None) -> str:
    """Mo video YouTube dau tien neu lay duoc, neu khong thi mo trang search."""
    video_url = _first_youtube_video_url(video)
    url = video_url or f"https://www.youtube.com/results?search_query={quote_plus(video)}"
    if browser:
        open_app(browser)
        time.sleep(1.5)
        if pyautogui and pyperclip:
            pyautogui.hotkey("ctrl", "l")
            pyperclip.copy(url)
            pyautogui.hotkey("ctrl", "v")
            pyautogui.press("enter")
            if video_url:
                return f"I am playing {video} on YouTube in {browser}, sir."
            return f"I opened YouTube in {browser} to search for {video}, sir."
    open_url(url)
    if video_url:
        return f"I am playing {video} on YouTube, sir."
    return f"I opened YouTube to search for {video}, sir."


def _first_youtube_video_url(query: str) -> str | None:
    """Lay URL video dau tien bang HTML search, khong can API key."""
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
        seen: set[str] = set()
        for video_id in re.findall(r'"videoId":"([A-Za-z0-9_-]{11})"', html):
            if video_id in seen:
                continue
            seen.add(video_id)
            return f"https://www.youtube.com/watch?v={video_id}"
    except Exception:
        return None
    return None


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
