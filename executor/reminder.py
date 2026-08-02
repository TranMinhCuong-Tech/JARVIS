"""
Reminder module - dat lich nhac nho, KHONG CAN API KEY.

Dung mot thread nen don gian de dem gio va hien thong bao he thong (qua
thu vien 'plyer', hoat dong tren ca Windows/macOS/Linux) khi den gio, thay vi
tich hop truc tiep vao Task Scheduler / cron (de giu code don gian, portable
va khong can quyen admin).
"""
import re
import threading
import time

try:
    from plyer import notification
except ImportError:
    notification = None


def _parse_delay_seconds(when_text: str):
    """Phan tich cac cum tu nhu 'in 10 minutes', 'in 2 hours' thanh so giay."""
    when_text = when_text.lower().strip()

    match = re.search(r"in\s+(\d+)\s*(second|minute|hour)s?", when_text)
    if not match:
        return None

    amount = int(match.group(1))
    unit = match.group(2)

    if unit == "second":
        return amount
    if unit == "minute":
        return amount * 60
    if unit == "hour":
        return amount * 3600
    return None


def set_reminder(when_text: str, message: str) -> str:
    """Dat mot reminder don gian. `when_text` vd: 'in 10 minutes'."""
    delay = _parse_delay_seconds(when_text)
    if delay is None:
        return (
            "Sorry sir, I could not understand the time. "
            "Please say something like 'remind me in 10 minutes to call John'."
        )

    def worker():
        time.sleep(delay)
        print(f"[Reminder]: {message}")
        if notification:
            try:
                notification.notify(
                    title="J.A.R.V.I.S Reminder",
                    message=message,
                    timeout=15,
                )
            except Exception as e:
                print(f"[Reminder Notification Error]: {e}")

    threading.Thread(target=worker, daemon=True).start()
    return f"Understood, sir. I will remind you {when_text}: {message}."
