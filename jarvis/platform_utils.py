from __future__ import annotations

import platform
import subprocess
import sys
import webbrowser
from pathlib import Path

from .compat import command_exists, hidden_subprocess_kwargs


OS_NAME = platform.system()


def open_url(url: str) -> bool:
    """Mo URL bang cong cu mac dinh cua he dieu hanh."""
    try:
        if OS_NAME == "Windows":
            subprocess.Popen(["cmd", "/c", "start", "", url], **hidden_subprocess_kwargs())
            return True
        if OS_NAME == "Darwin" and command_exists("open"):
            subprocess.Popen(["open", url])
            return True
        if OS_NAME == "Linux" and command_exists("xdg-open"):
            subprocess.Popen(["xdg-open", url])
            return True
    except Exception:
        pass
    return webbrowser.open(url)


def app_dir() -> Path:
    """Thu muc goc ung dung, ho tro ca khi dong goi thanh exe."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent
