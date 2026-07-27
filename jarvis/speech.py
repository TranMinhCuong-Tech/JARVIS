from __future__ import annotations

import threading


def speak(text: str) -> str:
    """Read assistant output aloud and mirror it to stdout."""
    print(text)
    try:
        import pyttsx3

        engine = pyttsx3.init()
        voices = engine.getProperty("voices")
        if voices:
            engine.setProperty("voice", voices[0].id)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
        return ""
    except Exception as exc:
        return (
            "Text-to-speech could not play audio. Please install pyttsx3 and "
            f"check your speaker output/system voice settings. Details: {exc}"
        )


class Speaker:
    """Noi phan hoi bang pyttsx3 neu co san."""

    def __init__(self) -> None:
        self.error = ""
        try:
            import pyttsx3

            self.engine = pyttsx3.init()
            self.available = True
            self._lock = threading.Lock()
        except Exception as exc:
            self.engine = None
            self.available = False
            self.error = (
                "Text-to-speech is not available. Please install pyttsx3 and check your "
                f"system voice settings. Details: {exc}"
            )
            self._lock = threading.Lock()

    def say(self, text: str) -> str:
        if not self.available or not self.engine:
            return self.error or "Text-to-speech is not available on this computer."
        try:
            with self._lock:
                self.engine.say(text)
                self.engine.runAndWait()
            return ""
        except Exception:
            return "Text-to-speech could not play audio. Please check your speaker output and system voice settings."


class VoiceRecognizer:
    """Nhan giong noi bang SpeechRecognition.

    Ghi chu:
    - Microphone cua SpeechRecognition can mot backend audio tren may.
    - Neu cai duoc pocketsphinx thi co the nhan offline.
    - Neu khong co pocketsphinx, thu vien se dung Google Web Speech.
      Cach nay khong can API key, nhung can internet.
    """

    def __init__(self) -> None:
        self.error = ""
        try:
            import speech_recognition as sr

            self.sr = sr
            self.recognizer = sr.Recognizer()
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 1.1
            self.recognizer.non_speaking_duration = 0.5
            self.recognizer.phrase_threshold = 0.25
            self.available = True
        except Exception as exc:
            self.sr = None
            self.recognizer = None
            self.available = False
            self.error = str(exc)

    def listen_once(self, language: str = "en-US") -> tuple[str, str]:
        """Nghe mot cau lenh va tra ve (text, error).

        Ham nay duoc goi trong thread rieng de khong lam treo UI.
        """
        if not self.available:
            return "", "Speech recognition is not ready."
        try:
            with self.sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.7)
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=12)
        except Exception:
            audio, audio_error = self._record_with_sounddevice()
            if not audio:
                return "", audio_error

        try:
            # Thu ca tieng Anh va tieng Viet vi nguoi dung co the noi xen ke.
            google_errors = []
            for candidate_language in (language, "vi-VN"):
                try:
                    return self.recognizer.recognize_google(audio, language=candidate_language), ""
                except self.sr.UnknownValueError:
                    google_errors.append("unknown")
                except Exception as exc:
                    google_errors.append(str(exc))

            # Fallback offline neu pocketsphinx co san.
            try:
                return self.recognizer.recognize_sphinx(audio), ""
            except Exception:
                if google_errors and all(error == "unknown" for error in google_errors):
                    return "", "I could not understand the voice command."
                return "", "Voice recognition could not process that request, sir."
        except self.sr.UnknownValueError:
            return "", "I could not understand the voice command."
        except Exception as exc:
            return "", f"Voice recognition could not process that request, sir."

    def _record_with_sounddevice(self, max_seconds: float = 10.0, sample_rate: int = 16000):
        """Thu am bang sounddevice voi VAD don gian de nghe cau dai hon."""
        try:
            import numpy as np
            import sounddevice as sd

            chunks = []
            block = int(0.25 * sample_rate)
            silence_blocks = 0
            heard_voice = False
            threshold = 450
            with sd.InputStream(samplerate=sample_rate, channels=1, dtype="int16") as stream:
                for _ in range(int(max_seconds / 0.25)):
                    data, _overflowed = stream.read(block)
                    arr = np.asarray(data).reshape(-1)
                    level = float(np.abs(arr).mean())
                    if level > threshold:
                        heard_voice = True
                        silence_blocks = 0
                    elif heard_voice:
                        silence_blocks += 1
                    if heard_voice:
                        chunks.append(arr.copy())
                    if heard_voice and silence_blocks >= 5:
                        break
            if not chunks:
                return None, "No voice was detected."
            pcm = np.concatenate(chunks).astype("int16").tobytes()
            return self.sr.AudioData(pcm, sample_rate, 2), ""
        except Exception as exc:
            return None, f"Could not record from the microphone: {exc}"
