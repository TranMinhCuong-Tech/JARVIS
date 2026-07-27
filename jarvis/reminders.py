from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class ReminderManager:
    """Schedules simple delayed reminders/timers and reports them back via a callback."""

    on_fire: Callable[[str], None]
    _active: list[threading.Timer] = field(default_factory=list)

    def schedule(self, minutes: float, message: str) -> str:
        seconds = max(1.0, minutes * 60)
        timer = threading.Timer(seconds, self._fire, args=(message,))
        timer.daemon = True
        timer.start()
        self._active.append(timer)

        if minutes < 1:
            when = f"{int(seconds)} seconds"
        elif minutes == int(minutes):
            when = f"{int(minutes)} minute{'s' if minutes != 1 else ''}"
        else:
            when = f"{minutes:g} minutes"

        if message:
            return f"Reminder set, sir. In {when} I will remind you to {message}."
        return f"Timer set, sir. I will notify you in {when}."

    def _fire(self, message: str) -> None:
        if message:
            self.on_fire(f"Reminder, sir: {message}")
        else:
            self.on_fire("Sir, your timer is done.")
