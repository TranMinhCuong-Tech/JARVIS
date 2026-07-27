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
    return f"Sir, CPU is at {cpu:.0f} percent, memory is at {ram:.0f} percent, and disk usage is {disk:.0f} percent."


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
