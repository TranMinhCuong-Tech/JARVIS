from __future__ import annotations

import platform
import subprocess

from .platform_utils import hidden_subprocess_kwargs


SYSTEM = platform.system()


def lock_screen() -> str:
    """Lock the current desktop session."""
    try:
        if SYSTEM == "Windows":
            subprocess.Popen(
                ["rundll32.exe", "user32.dll,LockWorkStation"],
                **hidden_subprocess_kwargs(),
            )
        elif SYSTEM == "Darwin":
            subprocess.Popen(
                [
                    "osascript",
                    "-e",
                    'tell application "System Events" to keystroke "q" using {control down, command down}',
                ]
            )
        else:
            subprocess.Popen(["loginctl", "lock-session"])
        return "I locked the screen, sir."
    except Exception as exc:
        return f"I could not lock the screen, sir. Details: {exc}"


def sleep_computer() -> str:
    """Put the computer to sleep."""
    try:
        if SYSTEM == "Windows":
            subprocess.Popen(
                ["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"],
                **hidden_subprocess_kwargs(),
            )
        elif SYSTEM == "Darwin":
            subprocess.Popen(["pmset", "sleepnow"])
        else:
            subprocess.Popen(["systemctl", "suspend"])
        return "I am putting the computer to sleep, sir."
    except Exception as exc:
        return f"I could not put the computer to sleep, sir. Details: {exc}"


def shutdown_computer() -> str:
    """Shut down the computer immediately."""
    try:
        if SYSTEM == "Windows":
            subprocess.Popen(["shutdown", "/s", "/t", "0"], **hidden_subprocess_kwargs())
        elif SYSTEM == "Darwin":
            subprocess.Popen(["osascript", "-e", 'tell application "System Events" to shut down'])
        else:
            subprocess.Popen(["systemctl", "poweroff"])
        return "I am shutting down the computer, sir."
    except Exception as exc:
        return f"I could not shut down the computer, sir. Details: {exc}"
