from __future__ import annotations

import os
import platform
import shutil
import subprocess
from collections.abc import Sequence


SYSTEM = platform.system()


def is_windows() -> bool:
    return SYSTEM == "Windows"


def is_macos() -> bool:
    return SYSTEM == "Darwin"


def is_linux() -> bool:
    return SYSTEM == "Linux"


def hidden_subprocess_kwargs() -> dict:
    if is_windows():
        return {"creationflags": subprocess.CREATE_NO_WINDOW}
    return {}


def command_exists(command: str) -> bool:
    return shutil.which(command) is not None


def has_desktop_session() -> bool:
    if is_windows() or is_macos():
        return True
    return bool(os.getenv("DISPLAY") or os.getenv("WAYLAND_DISPLAY"))


def run_available(commands: Sequence[Sequence[str]], timeout: int = 8) -> bool:
    for command in commands:
        if not command:
            continue
        binary = command[0]
        if not command_exists(binary) and not (is_windows() and binary.lower().endswith((".exe", ".com", ".bat", ".cmd"))):
            continue
        try:
            subprocess.Popen(
                list(command),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                **hidden_subprocess_kwargs(),
            )
            return True
        except Exception:
            continue
    return False
