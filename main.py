import threading
import time
from collections import deque
from datetime import datetime
from difflib import SequenceMatcher
import tkinter as tk

# Import cac module chinh theo dung cau truc du an
from agent.decision_engine import DecisionEngine
from core.asr import ASRHandler
from core.context import ContextMemory
from nlu.intent_parser import NaturalLanguageUnderstanding
from core.tts import TextToSpeech
from executor.actions import ActionExecutor
from gui import JarvisGUI


# Ham tinh do tuong dong giua 2 chuoi (0.0 -> 1.0)
def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def main():
    root = tk.Tk()

    # 1. Khoi tao cac thanh phan phu thuoc (Dependencies)
    context = ContextMemory()
    executor = ActionExecutor()
    tts = TextToSpeech()

    # NLU Handler dung de trich xuat Intent & Entities tu cau noi nguoi dung
    nlu = NaturalLanguageUnderstanding()

    # 2. Khoi tao DecisionEngine
    engine = DecisionEngine(context=context, executor=executor, tts=tts)

    # 3. Khoi tao Giao dien GUI qua cau 3D
    gui = JarvisGUI(root, on_submit_callback=None)

    # Dang ky listener de GUI biet khi Agent dang phat am thanh
    tts.register_speaking_listener(gui.set_speaking)

    # 4. Co che chong lap lenh manh me (anti-feedback loop)
    is_processing = False
    recent_commands = deque(maxlen=10)  # Luu 10 cau lenh gan nhat
    COOLDOWN_SECONDS = 5.0  # Thoi gian cho giua cac cau lenh giong nhau
    TTS_BLOCK_SECONDS = 3.0  # Thoi gian khoa nhan lenh sau khi TTS noi xong
    SIMILARITY_THRESHOLD = 0.55  # Nguong tuong dong voi phan hoi TTS

    # Cac tu khoa thuong xuat hien trong phan hoi TTS (de loc echo nhanh)
    RESPONSE_KEYWORDS = [
        "playing", "opening", "searching", "closed", "could not find",
        "increased", "decreased", "toggled", "screenshot", "written",
        "according", "current time", "today is", "ip address",
        "locking", "shutting down", "putting", "goodbye"
    ]

    def should_ignore_command(cmd: str) -> bool:
        """Kiem tra xem cau lenh co nen bi bo qua khong."""
        cmd_lower = cmd.lower().strip()
        now = time.time()

        # 1. Neu TTS dang noi -> bo qua
        if tts.speaking:
            print(f"[Filter]: TTS is speaking, ignored: '{cmd_lower}'")
            return True

        # 2. Neu vua moi noi xong trong vong TTS_BLOCK_SECONDS -> bo qua
        if now - tts.last_speak_time < TTS_BLOCK_SECONDS:
            print(f"[Filter]: Just finished speaking, ignored: '{cmd_lower}'")
            return True

        # 3. Kiem tra cau lenh vua duoc xu ly gan day (tranh lap do ASR nghe lai)
        for recent_cmd, recent_time in recent_commands:
            if recent_cmd.lower() == cmd_lower:
                if now - recent_time < COOLDOWN_SECONDS:
                    print(f"[Filter]: Duplicate command ignored: '{cmd_lower}'")
                    return True

        # 4. Kiem tra echo tu phan hoi TTS truoc do
        last_tts = tts.last_text.lower()
        if last_tts:
            # Neu do tuong dong cao -> bo qua
            sim = _similarity(cmd_lower, last_tts)
            if sim > SIMILARITY_THRESHOLD:
                print(f"[Filter]: Echo detected (sim={sim:.2f}), ignored: '{cmd_lower}'")
                return True

            # Neu cau lenh chua tu khoa cua phan hoi va do tuong dong trung binh
            for kw in RESPONSE_KEYWORDS:
                if kw in last_tts and kw in cmd_lower:
                    print(f"[Filter]: Keyword echo '{kw}', ignored: '{cmd_lower}'")
                    return True

        return False

    def process_command(command_text: str):
        nonlocal is_processing

        cmd_clean = command_text.strip()
        if not cmd_clean:
            return

        # Kiem tra neu dang xu ly lenh khac thi bo qua
        if is_processing:
            print(f"[Filter]: Busy processing, ignored: '{cmd_clean}'")
            return

        # Loc echo va lap
        if should_ignore_command(cmd_clean):
            return

        # Danh dau dang xu ly va luu vao lich su
        is_processing = True
        recent_commands.append((cmd_clean, time.time()))

        print(f"[User Input]: {cmd_clean}")
        gui.set_status(f"Processing: '{cmd_clean}'...")

        def worker():
            nonlocal is_processing
            try:
                # Trich xuat Intent va Entities tu van ban dau vao
                intent, entities, confidence = nlu.parse(cmd_clean)

                # Goi chinh xac phuong thuc process_and_execute
                should_continue = engine.process_and_execute(
                    intent=intent,
                    entities=entities,
                    confidence=confidence,
                    log_callback=lambda msg: print(f"[Log]: {msg}"),
                )

                gui.set_status("listening...")

                if not should_continue:
                    # Neu intent la EXIT, dong ung dung sau 2 giay
                    root.after(2000, root.destroy)

            except Exception as e:
                print(f"[Engine Error]: {e}")
                gui.set_status("Error processing request")
            finally:
                is_processing = False

        threading.Thread(target=worker, daemon=True).start()

    # Gan callback xu ly lenh cho GUI
    gui.on_submit_callback = process_command

    # 5. Phat Loi Chao Tu Dong khi vua mo ung dung (theo buoi)
    def speak_greeting():
        hour = datetime.now().hour
        if 0 <= hour < 12:
            period = "morning"
        elif 12 <= hour < 18:
            period = "afternoon"
        else:
            period = "evening"

        greeting_msg = (
            f"Good {period}, sir. Please tell me how can I help you, sir?"
        )
        gui.set_status(f"J.A.R.V.I.S: Online | {period}")
        try:
            tts.speak(greeting_msg)
        except Exception as e:
            print(f"[TTS Greeting Error]: {e}")

    threading.Thread(target=speak_greeting, daemon=True).start()

    # 6. Khoi chay Micro Tu Dong o Background (khong can an nut)
    # Micro luon hoat dong xuyen suot, khong bi tam dung
    try:
        asr = ASRHandler(on_speech_recognized=process_command)
        asr.start_listening_loop()
        gui.set_status("listening... (Microphone Active)")
    except Exception as e:
        print(f"[ASR Init Error]: {e}")
        gui.set_status("Text input only (Microphone unavailable)")

    root.mainloop()


if __name__ == "__main__":
    main()
