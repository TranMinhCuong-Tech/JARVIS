from core.context import ContextMemory
from core.tts import TextToSpeech
from executor.actions import ActionExecutor
from executor import weather as weather_mod
from executor import system_monitor
from executor import reminder as reminder_mod
from executor import desktop_control
from executor import auto_start
from executor import game_updater
from executor import clipboard_intel
from executor import code_helper as code_helper_mod
from executor import send_message


class DecisionEngine:
    """Component Decision Engine / Planner - Lap ke hoach va quyet dinh hanh dong."""

    # Nguong tin cay toi thieu de thuc thi truc tiep mot intent tu NLU.
    # NLU rule-based chi tra ve 0.95 (khop mau) hoac 0.30 (UNKNOWN), nen
    # nguong nay chu yeu dung de "bat" intent UNKNOWN va chuyen sang AI Brain.
    CONFIDENCE_THRESHOLD = 0.5

    def __init__(
        self,
        context: ContextMemory,
        executor: ActionExecutor,
        tts: TextToSpeech,
        llm=None,
    ):
        self.context = context
        self.executor = executor
        self.tts = tts
        # LLMBrain (tuy chon) - "bo nao AI" xu ly cau hoi tu do ma NLU
        # rule-based khong nhan dien duoc. Neu None hoac khong available,
        # Agent tu dong quay ve hanh vi cu (khong pha vo ung dung).
        self.llm = llm

    def process_and_execute(
        self,
        intent: str,
        entities: dict,
        confidence: float,
        log_callback=None,
    ) -> bool:
        def respond(msg: str):
            if log_callback:
                log_callback(f"Agent: {msg}")
            self.tts.speak(msg)

        # --- Day chinh la diem khac biet giua "voice command bot" va
        # "AI voice agent": khi khong nhan dien duoc intent ro rang (UNKNOWN
        # hoac do tin cay thap), Agent khong tra loi cau co dinh nua, ma nho
        # LLM (Claude) "suy nghi" va tra loi tu nhien theo dung nghia mot AI.
        if intent == "UNKNOWN" or confidence < self.CONFIDENCE_THRESHOLD:
            raw_text = entities.get("raw_text", "")
            llm_answer = self.llm.ask(raw_text) if self.llm else None
            if llm_answer:
                respond(llm_answer)
            else:
                respond(
                    "I heard you, but I'm not sure how to process that "
                    "request yet, sir. Could you please rephrase?"
                )
            return True

        if intent == "PLAY_YOUTUBE":
            media = entities.get("media_name")
            media = self.context.resolve_target(media)
            res_msg = self.executor.play_on_youtube(media)
            respond(res_msg)
            self.context.update("PLAY_YOUTUBE", media, True)

        elif intent == "PLAY_SPOTIFY":
            media = entities.get("media_name")
            media = self.context.resolve_target(media)
            res_msg = self.executor.play_on_spotify(media)
            respond(res_msg)
            self.context.update("PLAY_SPOTIFY", media, True)

        elif intent == "OPEN_APP":
            app_name = entities.get("app_name")
            app_name = self.context.resolve_target(app_name)
            if not app_name:
                respond("Which application would you like to open, sir?")
                return True
            respond(f"Opening {app_name}, sir.")
            success = self.executor.open_app(app_name)
            self.context.update("OPEN_APP", app_name, success)

        elif intent == "CLOSE_APP":
            app_name = entities.get("app_name")
            app_name = self.context.resolve_target(app_name)
            if not app_name:
                respond("Which application should I close, sir?")
                return True
            success = self.executor.close_app(app_name)
            msg = (
                f"Closed {app_name}, sir."
                if success
                else f"Could not find {app_name} running, sir."
            )
            respond(msg)
            self.context.update("CLOSE_APP", app_name, success)

        elif intent == "SYSTEM_CONTROL":
            action = entities.get("action", "")
            res_msg = self.executor.control_system(action)
            respond(res_msg)

        elif intent == "SEARCH_WEB":
            query = entities.get("query")
            # Truyen llm xuong Executor: neu Wikipedia khong co ket qua,
            # Agent se thu hoi Claude truoc khi phai mo Google lam phuong an
            # cuoi cung.
            res_msg = self.executor.search_web(query, llm=self.llm)
            respond(res_msg)

        elif intent == "TAKE_NOTE":
            content = entities.get("content")
            res_msg = self.executor.take_note(content)
            respond(res_msg)

        # --- Cac tinh nang moi ---
        elif intent == "TIME":
            respond(self.executor.get_time())

        elif intent == "DATE":
            respond(self.executor.get_date())

        elif intent == "IP_ADDRESS":
            respond(self.executor.get_ip_address())

        elif intent == "LOCK":
            respond(self.executor.lock_computer())

        elif intent == "SHUTDOWN":
            respond(self.executor.shutdown_computer())

        elif intent == "SLEEP":
            respond(self.executor.sleep_computer())

        elif intent == "WEATHER":
            city = entities.get("city") or self.context.resolve_target(None)
            if not city:
                respond("Which city's weather would you like, sir?")
                return True
            respond(weather_mod.get_weather(city))

        elif intent == "SYSTEM_STATS":
            respond(system_monitor.get_system_stats())

        elif intent == "SET_REMINDER":
            when = entities.get("when", "")
            message = entities.get("message", "")
            respond(reminder_mod.set_reminder(when, message))

        elif intent == "BRIGHTNESS":
            direction = entities.get("direction", "up")
            respond(desktop_control.set_brightness(direction))

        elif intent == "WIFI_TOGGLE":
            state = entities.get("state", "on")
            respond(desktop_control.toggle_wifi(state))

        elif intent == "DESKTOP_CONTROL":
            action = entities.get("action", "")
            if "switch" in action or "alt tab" in action:
                respond(desktop_control.switch_window())
            else:
                respond(desktop_control.show_desktop())

        elif intent == "AUTO_START":
            if entities.get("enable", True):
                respond(auto_start.enable_auto_start())
            else:
                respond(auto_start.disable_auto_start())

        elif intent == "GAME_UPDATE":
            platform_name = entities.get("platform", "steam")
            respond(game_updater.update_games(platform_name))

        elif intent == "CLIPBOARD_TOOL":
            action = entities.get("action", "")
            respond(clipboard_intel.process_clipboard(action, self.llm))

        elif intent == "CODE_HELPER":
            request = entities.get("request", "")
            respond(code_helper_mod.code_helper(request, self.llm))

        elif intent == "SEND_MESSAGE":
            platform_name = entities.get("platform", "whatsapp")
            message = entities.get("message", "")
            if platform_name == "telegram":
                respond(send_message.send_telegram(message))
            else:
                contact = entities.get("contact", "")
                respond(send_message.send_whatsapp(contact, message))

        elif intent == "EXIT":
            respond("Goodbye sir. Have a productive day.")
            return False

        else:
            respond(
                "I heard you, but I'm not sure how to process that request yet, sir."
            )

        return True
