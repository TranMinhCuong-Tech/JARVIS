from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Callable

from .app_launcher import close_app, open_app
from .automation import find_whatsapp_contact, play_spotify, play_youtube, send_message_flow, send_whatsapp_message
from .calculator import calculate
from .camera import open_camera
from .fun import random_joke, random_quote
from .knowledge import public_ip_address, wikipedia_summary
from .media_control import mute, next_track, play_pause, previous_track, volume_down, volume_up
from .platform_utils import open_url
from .power_control import lock_screen, shutdown_computer, sleep_computer
from .reminders import ReminderManager
from .screenshot import take_screenshot
from .system_info import battery_text, current_date_text, current_datetime_text, current_time_text, status_text
from .translator import translate_text
from .user_memory import UserMemory
from .weather import weather_summary


@dataclass
class PendingMessage:
    platform: str
    receiver: str
    message: str = ""
    waiting_for: str = "message"


@dataclass
class PendingConfirmation:
    action: str
    label: str


class CommandRouter:
    """Bo nao local cua JARVIS. Tat ca logic deu o day de de sua va mo rong."""

    def __init__(self, on_reminder: Callable[[str], None] | None = None) -> None:
        self.pending_message: PendingMessage | None = None
        self.pending_confirmation: PendingConfirmation | None = None
        self.memory = UserMemory()
        self.sleeping = False
        self.reminders = ReminderManager(on_fire=on_reminder or (lambda message: None))

    def handle(self, text: str) -> str:
        raw = text.strip()
        raw = self._normalize_transcript(raw)
        lower = raw.lower()
        normalized = self._plain_text(lower)

        if not raw:
            return "I am listening, sir."
        if normalized in {"bye", "goodbye", "you can sleep", "sleep", "tam biet"}:
            self.sleeping = True
            return "have a good day sir!"

        if self.pending_confirmation:
            return self._continue_confirmation_flow(raw)

        if self.pending_message:
            return self._continue_message_flow(raw)

        remember_response = self._handle_memory_command(raw)
        if remember_response:
            return remember_response

        if normalized in {"help", "commands", "help commands", "what can you do"}:
            return self._help_text()

        if self._asks_datetime(normalized):
            return current_datetime_text()
        if self._asks_time(normalized):
            return current_time_text()
        if self._asks_date(normalized):
            return current_date_text()

        if self._asks_lock_screen(normalized):
            self.pending_confirmation = PendingConfirmation("lock", "lock the screen")
            return "Please confirm, sir. Lock the screen now? Say yes or no."
        if self._asks_sleep_computer(normalized):
            self.pending_confirmation = PendingConfirmation("sleep", "put the computer to sleep")
            return "Please confirm, sir. Put the computer to sleep now? Say yes or no."
        if self._asks_shutdown_computer(normalized):
            self.pending_confirmation = PendingConfirmation("shutdown", "shut down the computer")
            return "Please confirm, sir. Shut down the computer now? Say yes or no."

        if self._asks_ip_address(normalized):
            return public_ip_address()

        if "battery" in normalized or "pin" in normalized:
            return battery_text()

        if "wikipedia" in normalized:
            topic = self._clean_wikipedia_query(raw)
            return wikipedia_summary(topic)

        weather_match = re.search(r"\bweather\b(?:\s+(?:in|for|at)\s+(.+))?", raw, flags=re.I)
        if weather_match or "thoi tiet" in normalized:
            city = weather_match.group(1).strip() if weather_match and weather_match.group(1) else ""
            return weather_summary(city)

        if any(phrase in normalized for phrase in ("tell me a joke", "make me laugh", "say something funny", "ke chuyen cuoi")):
            return random_joke()
        if any(phrase in normalized for phrase in ("inspire me", "give me a quote", "motivate me", "cho toi cau noi")):
            return random_quote()

        calc_match = re.search(r"^(?:calculate|compute|what is|what's|tinh)\s+(.+)$", raw, flags=re.I)
        if calc_match and re.search(r"\d", calc_match.group(1)):
            return calculate(calc_match.group(1))

        note_match = re.search(r"^(?:take a note|note that|add a note|ghi chu)\s*[:\-]?\s*(.+)$", raw, flags=re.I)
        if note_match:
            self.memory.add_note(note_match.group(1).strip())
            return "I have saved that note, sir."
        if any(phrase in normalized for phrase in ("read my notes", "what are my notes", "list my notes", "doc ghi chu")):
            notes = self.memory.list_notes()
            if not notes:
                return "You do not have any saved notes, sir."
            joined = "; ".join(f"{index + 1}. {note}" for index, note in enumerate(notes))
            return f"Here are your notes, sir: {joined}."
        if any(phrase in normalized for phrase in ("clear my notes", "delete my notes", "xoa ghi chu")):
            self.memory.clear_notes()
            return "All notes have been cleared, sir."

        reminder_match = re.search(
            r"(?:remind me|set a reminder|nhac toi)\s+in\s+(\d+(?:\.\d+)?)\s*(second|minute|hour)s?\s*(?:to\s+(.+))?$",
            raw,
            flags=re.I,
        )
        if reminder_match:
            amount = float(reminder_match.group(1))
            unit = reminder_match.group(2).lower()
            task = (reminder_match.group(3) or "").strip()
            minutes = amount / 60 if unit == "second" else amount * 60 if unit == "hour" else amount
            return self.reminders.schedule(minutes, task)

        timer_match = re.search(r"(?:set a timer for|timer for|hen gio)\s+(\d+(?:\.\d+)?)\s*(second|minute|hour)s?", raw, flags=re.I)
        if timer_match:
            amount = float(timer_match.group(1))
            unit = timer_match.group(2).lower()
            minutes = amount / 60 if unit == "second" else amount * 60 if unit == "hour" else amount
            return self.reminders.schedule(minutes, "")

        if any(phrase in normalized for phrase in ("take a screenshot", "capture screen", "chup man hinh")):
            return take_screenshot()

        translate_match = re.search(r"^translate\s+(.+?)\s+(?:to|into)\s+(\w+)$", raw, flags=re.I)
        if translate_match:
            return translate_text(translate_match.group(1), translate_match.group(2))

        search_match = re.search(r"^(?:google|search google for|search for|search)\s+(.+)$", raw, flags=re.I)
        if search_match:
            query = search_match.group(1).strip()
            open_url(f"https://www.google.com/search?q={query.replace(' ', '+')}")
            return f"Here is what I found on Google for {query}, sir."

        if any(phrase in normalized for phrase in ("play music", "resume music", "pause music", "phat nhac", "tam dung nhac")):
            return play_pause()
        if any(phrase in normalized for phrase in ("next song", "next track", "skip song", "bai tiep theo")):
            return next_track()
        if any(phrase in normalized for phrase in ("previous song", "previous track", "last song", "bai truoc")):
            return previous_track()
        if any(phrase in normalized for phrase in ("volume up", "turn up the volume", "tang am luong")):
            return volume_up()
        if any(phrase in normalized for phrase in ("volume down", "turn down the volume", "giam am luong")):
            return volume_down()
        if any(phrase in normalized for phrase in ("mute", "unmute", "tat tieng")):
            return mute()

        if "spotify" in normalized and any(word in normalized for word in ("play", "phay", "phat", "choi")):
            song = self._strip_words(raw, [
                "play",
                "phay",
                "phat",
                "phát",
                "choi",
                "chơi",
                "song",
                "bai",
                "bài",
                "on spotify",
                "tren spotify",
                "trên spotify",
                "spotify",
            ])
            return play_spotify(song or "liked songs")

        if self._has_youtube(lower):
            browser = self._find_browser(lower)
            video = self._clean_youtube_query(raw)
            video = re.sub(r"\b(in|bang|tren)\s+(chrome|edge|firefox|safari|brave)\b", "", video, flags=re.I).strip()
            return play_youtube(video or "JARVIS AI", browser)

        msg_match = re.search(r"(?:send message|gui tin|nhan tin)\s+(?:to|for|cho)?\s*(.*?)\s+(?:on|tren|bang)\s+(.+)", raw, flags=re.I)
        if msg_match:
            receiver = msg_match.group(1).strip() or "nguoi nhan"
            platform = msg_match.group(2).strip()
            if "whatsapp" in platform.lower():
                found, response = find_whatsapp_contact(receiver)
                if found:
                    self.pending_message = PendingMessage(platform="whatsapp", receiver=receiver, waiting_for="message")
                return response
            self.pending_message = PendingMessage(platform=platform, receiver=receiver)
            return f"What message would you like me to send to {receiver} on {platform}, sir?"

        if "system status" in lower or "may tinh" in lower or "cpu" in lower:
            return status_text()

        if any(device in normalized for device in ("camera", "webcam", "may anh")) and any(
            word in normalized for word in ("open", "mo", "bat")
        ):
            return open_camera()

        match = re.search(r"(?:close|dong)\s+(.+)", lower)
        if match:
            app_name = match.group(1).strip()
            self.pending_confirmation = PendingConfirmation(f"close:{app_name}", f"close {app_name}")
            return f"Please confirm, sir. Close {app_name}? Say yes or no."

        match = re.search(r"(?:open|mo)\s+(.+)", lower)
        if match:
            return open_app(match.group(1))

        return "I don't understand! Please tell me against! sir"

    def _continue_confirmation_flow(self, raw: str) -> str:
        confirmation = self.pending_confirmation
        assert confirmation is not None
        lower = self._plain_text(raw.lower())

        if lower in {"yes", "y", "sure", "ok", "confirm", "do it", "co", "dong y"}:
            self.pending_confirmation = None
            if confirmation.action == "lock":
                return lock_screen()
            if confirmation.action == "sleep":
                return sleep_computer()
            if confirmation.action == "shutdown":
                return shutdown_computer()
            if confirmation.action.startswith("close:"):
                return close_app(confirmation.action.split(":", 1)[1])
            return "Confirmed, sir."

        if lower in {"no", "n", "cancel", "huy", "khong"}:
            self.pending_confirmation = None
            return f"Cancelled {confirmation.label}, sir."

        return f"Please say yes to {confirmation.label}, or no to cancel, sir."

    def _continue_message_flow(self, raw: str) -> str:
        flow = self.pending_message
        assert flow is not None
        lower = raw.lower()

        if flow.waiting_for == "message":
            flow.message = raw
            flow.waiting_for = "confirm"
            return f"Please confirm, sir. Send this message to {flow.receiver} on {flow.platform}: '{flow.message}'? Say yes or no."

        if flow.waiting_for == "confirm":
            if lower in {"yes", "y", "sure", "ok", "send", "gui", "co", "dong y"}:
                self.pending_message = None
                if "whatsapp" in flow.platform.lower():
                    return send_whatsapp_message(flow.message)
                return send_message_flow(flow.platform, flow.receiver, flow.message)
            if lower in {"no", "n", "not sure", "cancel", "huy", "khong"}:
                self.pending_message = None
                return "Message cancelled, sir."
            return "Please say yes to send it, or no to cancel, sir."

        self.pending_message = None
        return "The pending action has been cancelled, sir."

    def _handle_memory_command(self, raw: str) -> str | None:
        remember = re.search(
            r"^(?:remember that|remember|nho rang|nhớ rằng)\s+(.+?)\s+(?:is|la|là)\s+(.+)$",
            raw,
            flags=re.I,
        )
        if remember:
            key = self._plain_text(remember.group(1).lower()).replace(" ", "_")
            value = remember.group(2).strip()
            self.memory.remember_preference(key, value)
            return f"I will remember that {remember.group(1).strip()} is {value}, sir."

        recall = re.search(r"^(?:what is|what's|recall|nho gi ve|nhớ gì về)\s+(.+)$", raw, flags=re.I)
        if recall:
            key_text = recall.group(1).strip().rstrip("?")
            key = self._plain_text(key_text.lower()).replace(" ", "_")
            value = self.memory.preference(key)
            if value:
                return f"You told me {key_text} is {value}, sir."
            return f"I do not have a memory for {key_text} yet, sir."

        return None

    @staticmethod
    def _help_text() -> str:
        return (
            "I can open or close apps, play Spotify or YouTube, check time, date, system status and battery, "
            "open the camera, search Wikipedia and Google, report the weather, tell a joke or a quote, "
            "do quick math, take and read notes, set reminders and timers, take screenshots, control media "
            "playback and volume, translate text, send WhatsApp messages, and remember simple preferences, sir. "
            "Risky actions like shutdown, sleep, lock, and close app require confirmation."
        )

    @staticmethod
    def _find_browser(lower: str) -> str | None:
        for browser in ("chrome", "edge", "firefox", "safari", "brave"):
            if browser in lower:
                return browser
        return None

    @staticmethod
    def _normalize_transcript(text: str) -> str:
        """Sua nhanh mot so loi STT thuong gap truoc khi parse lenh."""
        replacements = {
            r"\byou\s*tube\b": "youtube",
            r"\byout+\s*tube\b": "youtube",
            r"\byouttube\b": "youtube",
            r"\byoutub\b": "youtube",
            r"\bstartboy\b": "starboy",
        }
        result = text
        for pattern, value in replacements.items():
            result = re.sub(pattern, value, result, flags=re.I)
        return " ".join(result.split())

    @staticmethod
    def _plain_text(text: str) -> str:
        """Bo dau tieng Viet de parser hieu transcript bi nhan sai nhe."""
        without_marks = unicodedata.normalize("NFD", text)
        without_marks = "".join(char for char in without_marks if unicodedata.category(char) != "Mn")
        without_marks = without_marks.replace("đ", "d").replace("Đ", "D")
        return " ".join(without_marks.split())

    @staticmethod
    def _has_youtube(lower: str) -> bool:
        return bool(re.search(r"\b(you\s*tube|youtube|youttube|youtub)\b", lower))

    @staticmethod
    def _clean_youtube_query(text: str) -> str:
        """Tach phan ten video/bai hat khoi cau lenh YouTube."""
        result = re.sub(r"\b(open|mo|play|phat|choi|watch|xem)\b", " ", text, flags=re.I)
        result = re.sub(r"\b(song|video|clip)\b", " ", result, flags=re.I)
        result = re.sub(r"\b(on|in|tren|bang)\s+(you\s*tube|youtube|youttube|youtub)\b", " ", result, flags=re.I)
        result = re.sub(r"\b(you\s*tube|youtube|youttube|youtub)\b", " ", result, flags=re.I)
        result = re.sub(r"\b(on|in|tren|bang)\s*$", " ", result, flags=re.I)
        return " ".join(result.split())

    @staticmethod
    def _clean_wikipedia_query(text: str) -> str:
        """Tach chu de can tim khoi cau hoi Wikipedia."""
        result = re.sub(r"\bwikipedia\b", " ", text, flags=re.I)
        result = result.replace("?", " ")
        result = re.sub(r"^\s*(what|who|where|when)\s+(is|are|was|were)\s+", " ", result, flags=re.I)
        result = re.sub(r"^\s*(tell me about|search for|search|look up)\s+", " ", result, flags=re.I)
        result = re.sub(r"\b(on|in|from|tren|tai)\b\s*$", " ", result, flags=re.I)
        return " ".join(result.split())

    @staticmethod
    def _asks_time(lower: str) -> bool:
        time_phrases = (
            "what time is it",
            "time is it",
            "what is the time",
            "tell me the time",
            "time now",
            "current time",
            "what time",
            "may gio",
            "bay gio la may gio",
            "gio hien tai",
        )
        return any(phrase in lower for phrase in time_phrases) or lower.strip() in {"time", "clock"}

    @staticmethod
    def _asks_date(lower: str) -> bool:
        date_phrases = (
            "what is day today",
            "what day is today",
            "what date is today",
            "what is the date today",
            "what is today",
            "day today",
            "today date",
            "date today",
            "thu may hom nay",
            "hom nay ngay may",
            "hom nay la ngay nao",
            "ngay hom nay",
            "di day today",
        )
        return any(phrase in lower for phrase in date_phrases) or lower.strip() in {"date", "day", "today"}

    @staticmethod
    def _asks_datetime(lower: str) -> bool:
        return any(phrase in lower for phrase in (
            "date and time",
            "time and date",
            "what date and time",
            "what time and date",
            "ngay gio",
            "ngay va gio",
        ))

    @staticmethod
    def _asks_ip_address(lower: str) -> bool:
        return any(phrase in lower for phrase in (
            "ip address",
            "my ip",
            "public ip",
            "dia chi ip",
            "đia chi ip",
            "ip cua toi",
        ))

    @staticmethod
    def _asks_lock_screen(lower: str) -> bool:
        return any(phrase in lower for phrase in (
            "lock screen",
            "lock the screen",
            "khoa man hinh",
            "khoa may",
        ))

    @staticmethod
    def _asks_sleep_computer(lower: str) -> bool:
        return any(phrase in lower for phrase in (
            "sleep computer",
            "put computer to sleep",
            "put the computer to sleep",
            "sleep my computer",
            "cho may ngu",
            "dua may ve che do ngu",
        ))

    @staticmethod
    def _asks_shutdown_computer(lower: str) -> bool:
        return any(phrase in lower for phrase in (
            "shutdown computer",
            "shut down computer",
            "shutdown my computer",
            "shut down my computer",
            "turn off computer",
            "tat may",
            "tat may tinh",
        ))

    @staticmethod
    def _strip_words(text: str, words: list[str]) -> str:
        result = text
        for word in sorted(words, key=len, reverse=True):
            pattern = r"(?<!\w)" + re.escape(word) + r"(?!\w)"
            result = re.sub(pattern, " ", result, flags=re.I)
        return " ".join(result.split())
