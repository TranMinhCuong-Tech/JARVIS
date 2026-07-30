from core.context import ContextMemory
from core.tts import TextToSpeech
from executor.actions import ActionExecutor


class DecisionEngine:
    """Component Decision Engine / Planner - Lap ke hoach va quyet dinh hanh dong."""

    def __init__(
        self,
        context: ContextMemory,
        executor: ActionExecutor,
        tts: TextToSpeech,
    ):
        self.context = context
        self.executor = executor
        self.tts = tts

    def process(self, text: str) -> bool:
        """Ham nhan van ban tho, gia dinh NLU don gian hoac goi process_and_execute truc tiep."""
        # Gia dinh phan tich Intent don gian neu chua qua NLU
        cleaned_text = text.lower()
        intent = "PLAY_YOUTUBE"
        entities = {"media_name": text}

        if "spotify" in cleaned_text:
            intent = "PLAY_SPOTIFY"
        elif "open" in cleaned_text:
            intent = "OPEN_APP"
            entities = {"app_name": text.replace("open", "").strip()}

        return self.process_and_execute(
            intent=intent, entities=entities, confidence=1.0
        )

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
            res_msg = self.executor.search_web(query)
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

        elif intent == "EXIT":
            respond("Goodbye sir. Have a productive day.")
            return False

        else:
            respond(
                "I heard you, but I'm not sure how to process that request yet, sir."
            )

        return True
