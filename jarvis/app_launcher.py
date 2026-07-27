from __future__ import annotations

import platform
import shutil
import subprocess
import time

from .compat import command_exists, has_desktop_session, hidden_subprocess_kwargs

try:
    import pyautogui
except Exception:
    pyautogui = None


SYSTEM = platform.system()

APP_ALIASES: dict[str, dict[str, str]] = {
    "chrome": {"Windows": "chrome", "Darwin": "Google Chrome", "Linux": "google-chrome"},
    "edge": {"Windows": "msedge", "Darwin": "Microsoft Edge", "Linux": "microsoft-edge"},
    "firefox": {"Windows": "firefox", "Darwin": "Firefox", "Linux": "firefox"},
    "spotify": {"Windows": "Spotify", "Darwin": "Spotify", "Linux": "spotify"},
    "whatsapp": {"Windows": "WhatsApp", "Darwin": "WhatsApp", "Linux": "whatsapp"},
    "telegram": {"Windows": "Telegram", "Darwin": "Telegram", "Linux": "telegram"},
    "discord": {"Windows": "Discord", "Darwin": "Discord", "Linux": "discord"},
    "notepad": {"Windows": "notepad.exe", "Darwin": "TextEdit", "Linux": "gedit"},
    "calculator": {"Windows": "calc.exe", "Darwin": "Calculator", "Linux": "gnome-calculator"},
    "terminal": {"Windows": "wt", "Darwin": "Terminal", "Linux": "x-terminal-emulator"},
    "explorer": {"Windows": "explorer.exe", "Darwin": "Finder", "Linux": "nautilus"},
    "finder": {"Windows": "explorer.exe", "Darwin": "Finder", "Linux": "nautilus"},
    "settings": {"Windows": "ms-settings:", "Darwin": "System Settings", "Linux": "gnome-control-center"},
}


def normalize_app_name(name: str) -> str:
    """Doi ten nguoi dung noi sang ten ung dung tren tung OS."""
    key = name.lower().strip()
    if key in APP_ALIASES:
        return APP_ALIASES[key].get(SYSTEM, name)
    for alias, values in APP_ALIASES.items():
        if alias in key or key in alias:
            return values.get(SYSTEM, name)
    return name.strip()


def open_app(app_name: str) -> str:
    """Mo ung dung bang cach tot nhat tren OS hien tai."""
    if not has_desktop_session():
        return "I need a graphical desktop session to open applications, sir."

    target = normalize_app_name(app_name)
    if not target:
        return "Please tell me which application to open, sir."

    if SYSTEM == "Windows":
        return _open_windows(target, app_name)
    if SYSTEM == "Darwin":
        return _open_macos(target, app_name)
    return _open_linux(target, app_name)


def close_app(app_name: str) -> str:
    """Dong ung dung theo ten tien trinh. Lenh nay co the that bai neu OS chan quyen."""
    target = normalize_app_name(app_name)
    try:
        if SYSTEM == "Windows":
            exe = target if target.lower().endswith(".exe") else f"{target}.exe"
            subprocess.run(["taskkill", "/IM", exe, "/F"], capture_output=True, timeout=8, **hidden_subprocess_kwargs())
        elif SYSTEM == "Darwin":
            subprocess.run(["osascript", "-e", f'tell application "{target}" to quit'], capture_output=True, timeout=8)
        else:
            subprocess.run(["pkill", "-f", target], capture_output=True, timeout=8)
        return f"I requested {app_name} to close, sir."
    except Exception as exc:
        return f"I could not close {app_name}, sir: {exc}"


def _open_windows(target: str, original: str) -> str:
    if ":" in target:
        subprocess.Popen(["cmd", "/c", "start", "", target], **hidden_subprocess_kwargs())
        return f"I opened {original}, sir."

    if shutil.which(target) or shutil.which(target.split(".")[0]):
        subprocess.Popen(target, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"I opened {original}, sir."

    # Windows Search fallback: bam Win, go ten app, Enter.
    if pyautogui:
        old_failsafe = getattr(pyautogui, "FAILSAFE", True)
        pyautogui.FAILSAFE = False
        try:
            pyautogui.press("win")
            time.sleep(0.5)
            pyautogui.write(target, interval=0.03)
            time.sleep(0.7)
            pyautogui.press("enter")
            return f"I found and opened {original} with Windows Search, sir."
        except Exception as exc:
            return f"I could not use Windows Search to open {original}, sir: {exc}"
        finally:
            pyautogui.FAILSAFE = old_failsafe
    return f"I could not find {original}, sir. Install pyautogui to use Windows Search."


def _open_macos(target: str, original: str) -> str:
    if command_exists("open"):
        result = subprocess.run(["open", "-a", target], capture_output=True, timeout=8)
        if result.returncode == 0:
            return f"I opened {original}, sir."
    if pyautogui:
        pyautogui.hotkey("command", "space")
        time.sleep(0.4)
        pyautogui.write(target, interval=0.03)
        pyautogui.press("enter")
        return f"I found and opened {original} with Spotlight, sir."
    return f"I could not open {original}, sir."


def _open_linux(target: str, original: str) -> str:
    binary = shutil.which(target) or shutil.which(target.lower()) or shutil.which(target.lower().replace(" ", "-"))
    if binary:
        subprocess.Popen([binary], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"I opened {original}, sir."
    for launcher in ("gtk-launch", "gio"):
        if not command_exists(launcher):
            continue
        for desktop_name in (target.lower(), target.lower().replace(" ", "-"), target.lower().replace(" ", "")):
            command = [launcher, desktop_name] if launcher == "gtk-launch" else [launcher, "open", f"application://{desktop_name}.desktop"]
            result = subprocess.run(command, capture_output=True, timeout=5)
            if result.returncode == 0:
                return f"I opened {original}, sir."
    return f"I could not open {original}, sir. The application may not be installed."
