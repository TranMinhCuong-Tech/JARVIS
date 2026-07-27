from __future__ import annotations

import platform
from datetime import datetime

try:
    import psutil
except Exception:
    psutil = None


def status_text() -> str:
    """Lay thong tin he thong ngan gon."""
    if not psutil:
        return f"Sir, this system is running {platform.system()} {platform.release()}. Install psutil for CPU and memory details."
    cpu = psutil.cpu_percent(interval=0.2)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    battery_note = _battery_fragment()
    return (
        f"Sir, CPU is at {cpu:.0f} percent, memory is at {ram:.0f} percent, "
        f"disk usage is {disk:.0f} percent{battery_note}."
    )


def battery_text() -> str:
    """Standalone battery report for laptops; desktops will get a graceful message."""
    if not psutil or not hasattr(psutil, "sensors_battery"):
        return "I could not read battery information on this system, sir."
    battery = psutil.sensors_battery()
    if battery is None:
        return "This machine does not report battery information, sir. It may be a desktop."
    state = "charging" if battery.power_plugged else "on battery power"
    return f"Battery is at {battery.percent:.0f} percent and the system is currently {state}, sir."


def _battery_fragment() -> str:
    if not psutil or not hasattr(psutil, "sensors_battery"):
        return ""
    battery = psutil.sensors_battery()
    if battery is None:
        return ""
    return f", and battery is at {battery.percent:.0f} percent"


def current_time_text() -> str:
    """Tra loi gio hien tai theo dong ho cua may."""
    now = datetime.now()
    return f"It is {now:%H:%M:%S}, sir."


def current_date_text() -> str:
    """Tra loi ngay thang nam hien tai theo dong ho cua may."""
    now = datetime.now()
    weekday = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ][now.weekday()]
    return f"Today is {weekday}, {now:%B %d, %Y}, sir."


def current_datetime_text() -> str:
    """Tra loi ca ngay va gio hien tai."""
    now = datetime.now()
    return f"Today is {now:%B %d, %Y}, and the time is {now:%H:%M:%S}, sir."


def day_period() -> str:
    """Tinh buoi trong ngay: morning, afternoon, evening."""
    hour = datetime.now().hour
    if 0 <= hour < 12:
        return "morning"
    if 12 <= hour < 18:
        return "afternoon"
    return "evening"
