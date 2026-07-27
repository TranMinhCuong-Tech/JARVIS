from __future__ import annotations

try:
    import pyautogui
except Exception:
    pyautogui = None


_KEY_MAP = {
    "play_pause": "playpause",
    "next": "nexttrack",
    "previous": "prevtrack",
    "volume_up": "volumeup",
    "volume_down": "volumedown",
    "mute": "volumemute",
}


def _press(action: str, friendly: str) -> str:
    if not pyautogui:
        return f"Please install pyautogui to control media, sir."
    key = _KEY_MAP[action]
    try:
        pyautogui.press(key)
        return f"{friendly}, sir."
    except Exception as exc:
        return f"I could not send the media key on this system, sir. Details: {exc}"


def play_pause() -> str:
    return _press("play_pause", "Toggled play and pause")


def next_track() -> str:
    return _press("next", "Skipped to the next track")


def previous_track() -> str:
    return _press("previous", "Went back to the previous track")


def volume_up() -> str:
    return _press("volume_up", "Volume increased")


def volume_down() -> str:
    return _press("volume_down", "Volume decreased")


def mute() -> str:
    return _press("mute", "Toggled mute")
