"""
Desktop / System Settings control - KHONG CAN API KEY.
Dieu khien do sang man hinh, bat/tat wifi, va thao tac cua so co ban.
Mot so chuc nang chi hoat dong day du tren Windows (dung os.system/netsh).
"""
import os
import platform
import pyautogui

try:
    import screen_brightness_control as sbc
except ImportError:
    sbc = None


def set_brightness(direction: str) -> str:
    """direction: 'up' hoac 'down'."""
    if not sbc:
        return "Brightness control is not available. Please install 'screen-brightness-control'."
    try:
        current = sbc.get_brightness(display=0)[0]
        step = 10
        new_value = current + step if direction == "up" else current - step
        new_value = max(0, min(100, new_value))
        sbc.set_brightness(new_value)
        return f"Brightness set to {new_value} percent, sir."
    except Exception as e:
        print(f"[Brightness Error]: {e}")
        return "Sorry sir, I could not adjust the brightness on this device."


def toggle_wifi(state: str) -> str:
    """state: 'on' hoac 'off'. Chi ho tro day du tren Windows qua netsh."""
    system = platform.system()
    if system == "Windows":
        interface = "Wi-Fi"
        cmd = f'netsh interface set interface "{interface}" {"enabled" if state == "on" else "disabled"}'
        result = os.system(cmd)
        if result == 0:
            return f"Wi-Fi turned {state}, sir."
        return "Sorry sir, I could not change the Wi-Fi state. Try running as Administrator."
    return f"Wi-Fi toggling is only automated on Windows in this build, sir."


def minimize_all_windows() -> str:
    pyautogui.hotkey("win", "d")
    return "All windows minimized, sir."


def switch_window() -> str:
    pyautogui.hotkey("alt", "tab")
    return "Switching window, sir."


def show_desktop() -> str:
    pyautogui.hotkey("win", "d")
    return "Showing desktop, sir."
