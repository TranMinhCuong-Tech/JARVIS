import pyttsx3
import threading
import time
from typing import Callable, List


class TextToSpeech:
    """
    Component TTS - Chuyen doi van ban thanh giong noi.
    Khoi tao engine moi moi lan noi de tranh loi hang doi COM tren Windows.
    Ho tro theo doi trang thai noi va noi dung de loc echo.
    """
    def __init__(self, rate: int = 175):
        self.rate = rate
        self._speaking = False
        self._last_speak_time = 0.0
        self._last_text = ""
        self._listeners: List[Callable[[bool], None]] = []

    def register_speaking_listener(self, callback: Callable[[bool], None]):
        """Dang ky listener de nhan biet trang thai dang noi (cho GUI)."""
        self._listeners.append(callback)

    def _notify(self, state: bool):
        for cb in self._listeners:
            try:
                cb(state)
            except Exception:
                pass

    @property
    def speaking(self) -> bool:
        return self._speaking

    @property
    def last_speak_time(self) -> float:
        return self._last_speak_time

    @property
    def last_text(self) -> str:
        return self._last_text

    def speak(self, text: str, callback=None) -> None:
        def _speak():
            print(f"[Agent]: {text}")
            self._speaking = True
            self._last_text = text
            self._notify(True)
            try:
                engine = pyttsx3.init("sapi5")
                voices = engine.getProperty("voices")
                if voices:
                    engine.setProperty("voice", voices[0].id)
                engine.setProperty("rate", self.rate)
                engine.say(text)
                engine.runAndWait()
                engine.stop()
            except Exception as e:
                print(f"[TTS Error]: {e}")
            self._speaking = False
            self._last_speak_time = time.time()
            self._notify(False)
            if callback:
                callback()

        # Chay TTS tren thread rieng de khong lam treo GUI
        threading.Thread(target=_speak, daemon=True).start()

    def speak_sync(self, text: str) -> None:
        """Noi dong bo dung khi can cho doc xong moi xu ly tiep."""
        self._speaking = True
        self._last_text = text
        self._notify(True)
        try:
            engine = pyttsx3.init("sapi5")
            voices = engine.getProperty("voices")
            if voices:
                engine.setProperty("voice", voices[0].id)
            engine.setProperty("rate", self.rate)
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            print(f"[TTS Error]: {e}")
        self._speaking = False
        self._last_speak_time = time.time()
        self._notify(False)
