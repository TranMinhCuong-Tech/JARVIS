import threading
from typing import Callable
import speech_recognition as sr


class ASRHandler:
    """
    Component ASR - Nhan dien giong noi tu microphone.
    Micro luon hoat dong xuyen suot, khong bi tam dung.
    Viec loc nhieu/echo se do phia xu ly lenh dam nhan.
    """

    def __init__(self, on_speech_recognized: Callable[[str], None] = None):
        self.recognizer = sr.Recognizer()
        self.on_speech_recognized = on_speech_recognized
        self.is_listening = False

    def start_listening_loop(self):
        """Khoi chay luong tu dong lang nghe giong noi lien tuc tu Micro."""
        self.is_listening = True
        thread = threading.Thread(target=self._listen_worker, daemon=True)
        thread.start()

    def _listen_worker(self):
        try:
            with sr.Microphone() as source:
                # Tu dong loc tieng on moi truong
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                print("[ASR]: Microphone is ACTIVE and Listening...")

                while self.is_listening:
                    try:
                        # Timeout ngan de co the kiem tra is_listening thuong xuyen
                        audio = self.recognizer.listen(source, phrase_time_limit=7.0, timeout=1.0)

                        # Thu nhan dien tieng Anh truoc, neu khong duoc chuyen sang tieng Viet
                        text = None
                        try:
                            text = self.recognizer.recognize_google(audio, language="en-US")
                        except sr.UnknownValueError:
                            try:
                                text = self.recognizer.recognize_google(audio, language="vi-VN")
                            except sr.UnknownValueError:
                                continue

                        if text and self.on_speech_recognized:
                            print(f"[ASR Recognized]: {text}")
                            self.on_speech_recognized(text)

                    except sr.WaitTimeoutError:
                        continue
                    except sr.RequestError as e:
                        print(f"[ASR Request Error]: {e}")
                    except Exception as e:
                        print(f"[ASR Loop Error]: {e}")
        except Exception as e:
            print(f"[ASR Init Error]: {e}")
