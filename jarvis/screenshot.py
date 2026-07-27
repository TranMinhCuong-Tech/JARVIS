from __future__ import annotations

import time
from pathlib import Path


def take_screenshot() -> str:
    """Capture the full screen and save it under Pictures/JARVIS_Screenshots."""
    try:
        from PIL import ImageGrab

        image = ImageGrab.grab()
    except Exception:
        try:
            import pyautogui

            image = pyautogui.screenshot()
        except Exception as exc:
            return f"I could not take a screenshot, sir. Please install Pillow or pyautogui. Details: {exc}"

    try:
        target_dir = Path.home() / "Pictures" / "JARVIS_Screenshots"
        target_dir.mkdir(parents=True, exist_ok=True)
        filename = target_dir / f"jarvis_{time.strftime('%Y%m%d_%H%M%S')}.png"
        image.save(filename)
        return f"Screenshot saved to {filename}, sir."
    except Exception as exc:
        return f"I captured the screen but could not save it, sir. Details: {exc}"
