import re
from typing import Dict, Any, Tuple


class NaturalLanguageUnderstanding:
    """
    Component NLU - Phan loai Intent va Trich xuat Entity tu van ban.
    """
    def __init__(self):
        self.intent_patterns = {
            "PLAY_YOUTUBE": [
                r"\b(play|watch)\s+(.+)\s+on\s+youtube\b",
                r"\b(open\s+youtube\s+and\s+play)\s+(.+)\b",
                r"\b(youtube\s+search|play\s+on\s+youtube)\s+(.+)\b",
                r"\b(open\s+youtube|go\s+to\s+youtube)\b"
            ],
            "PLAY_SPOTIFY": [
                r"\b(play|listen\s+to)\s+(.+)\s+on\s+spotify\b",
                r"\b(spotify\s+play)\s+(.+)\b",
                r"\b(open\s+spotify|go\s+to\s+spotify)\b"
            ],
            "OPEN_APP": [
                r"\b(open|launch|start|run)\s+(.+)",
                r"\b(i\s+want\s+to\s+use)\s+(.+)"
            ],
            "CLOSE_APP": [
                r"\b(close|exit|kill|dong)\s+(.+)",
                r"\b(stop)\s+(.+)"
            ],
            "SYSTEM_CONTROL": [
                r"\b(volume\s+up|increase\s+volume|louder)\b",
                r"\b(volume\s+down|decrease\s+volume|quieter)\b",
                r"\b(mute|unmute)\b",
                r"\b(take\s+screenshot|capture\s+screen)\b"
            ],
            "TAKE_NOTE": [
                r"\b(note\s+down|take\s+a\s+note|write\s+down|remember\s+that)\s+(.+)"
            ],
            "TIME": [
                r"\b(what\s+time\s+is\s+it|current\s+time|tell\s+me\s+the\s+time|what\'s\s+the\s+time)\b"
            ],
            "DATE": [
                r"\b(what\s+day\s+is\s+today|what\s+date\s+is\s+it|today\'s\s+date|what\s+is\s+today)\b"
            ],
            # IP_ADDRESS phai duoc dat truoc SEARCH_WEB, vi ca hai deu co the
            # khop voi cau bat dau bang "what is ..." (vd: "what is my address").
            # Neu de sau, SEARCH_WEB se "cuop" intent va mo trinh duyet tim kiem
            # thay vi tra loi IP truc tiep.
            "IP_ADDRESS": [
                r"\b(what\s+is|what\'s)\s+my\s+(ip\s+)?address\b",
                r"\b(what\s+is|what\'s)\s+my\s+ip\b",
                r"\bmy\s+ip\s+address\b",
                r"\bshow\s+my\s+(ip|ip\s+address|address)\b",
                r"\btell\s+me\s+my\s+(ip|address)\b",
                r"\bip\s+address\b"
            ],
            "SEARCH_WEB": [
                r"\b(search\s+for|google|find\s+info\s+about|lookup)\s+(.+)",
                r"\b(what\s+is|who\s+is|tell\s+me\s+about)\s+(.+)"
            ],
            "LOCK": [
                r"\b(lock\s+computer|lock\s+screen|lock\s+my\s+pc|lock\s+the\s+screen)\b"
            ],
            "SHUTDOWN": [
                r"\b(shutdown\s+computer|shut\s+down|turn\s+off\s+computer|power\s+off)\b"
            ],
            "SLEEP": [
                r"\b(sleep|go\s+to\s+sleep|standby|hibernate)\b"
            ],
            "EXIT": [
                r"\b(exit|quit|bye|goodbye|stop\s+agent|close\s+agent)\b",
                r"\b(stop)\b"
            ],

            # --- Cac intent moi (khong can API key, tru CLIPBOARD_TOOL / CODE_HELPER) ---
            "WEATHER": [
                r"\b(weather|forecast)\s+(?:in|at|for)\s+(.+)",
                r"\b(what\'s|what\s+is)\s+the\s+weather\s+(?:in|at|for)\s+(.+)",
                r"\b(weather)\b"
            ],
            "SYSTEM_STATS": [
                r"\b(system\s+stats|how\'s\s+my\s+(pc|computer)\s+doing|check\s+(cpu|ram|memory)|hardware\s+status)\b"
            ],
            "SET_REMINDER": [
                r"\bremind\s+me\s+(in\s+\d+\s*(?:second|minute|hour)s?)\s+to\s+(.+)",
                r"\bset\s+a\s+reminder\s+(in\s+\d+\s*(?:second|minute|hour)s?)\s+to\s+(.+)"
            ],
            "BRIGHTNESS": [
                r"\b(brightness\s+up|increase\s+brightness|brighter)\b",
                r"\b(brightness\s+down|decrease\s+brightness|dimmer)\b"
            ],
            "WIFI_TOGGLE": [
                r"\b(turn\s+on\s+wifi|enable\s+wifi|wifi\s+on)\b",
                r"\b(turn\s+off\s+wifi|disable\s+wifi|wifi\s+off)\b"
            ],
            "DESKTOP_CONTROL": [
                r"\b(minimize\s+all|show\s+desktop)\b",
                r"\b(switch\s+window|alt\s+tab)\b"
            ],
            "AUTO_START": [
                r"\b(enable\s+auto\s*.?start|start\s+with\s+windows|start\s+on\s+boot)\b",
                r"\b(disable\s+auto\s*.?start|don\'t\s+start\s+with\s+windows)\b"
            ],
            "GAME_UPDATE": [
                r"\b(update\s+(?:my\s+)?games\s+on\s+(steam|epic))\b",
                r"\b(check\s+(?:for\s+)?(steam|epic)\s+updates)\b"
            ],
            "CLIPBOARD_TOOL": [
                r"\b(translate|summarize|explain|fix)\s+(?:my|the)?\s*clipboard\b"
            ],
            "CODE_HELPER": [
                r"\b(help\s+me\s+code|code\s+helper|review\s+my\s+code|write\s+(?:me\s+)?(?:a\s+)?(?:function|script|code))\s*(.*)"
            ],
            "SEND_MESSAGE": [
                r"\b(?:send|message)\s+(.+?)\s+on\s+whatsapp\s+(?:saying|that says)\s+(.+)",
                r"\bsend\s+(?:a\s+)?whatsapp\s+(?:message\s+)?to\s+(.+?)\s+(?:saying|that says)\s+(.+)",
                r"\bsend\s+(?:a\s+)?telegram\s+message\s+(?:saying|that says)\s+(.+)",
            ],
        }

    def parse(self, text: str) -> Tuple[str, Dict[str, Any], float]:
        text = text.strip().lower()
        if not text:
            return "UNKNOWN", {}, 0.0

        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    entities = {}
                    groups = match.groups()

                    if intent == "PLAY_YOUTUBE":
                        if len(groups) >= 2 and groups[1]:
                            entities["media_name"] = groups[1].strip()
                        elif len(groups) == 1 and groups[0] and groups[0] not in ["open youtube", "go to youtube"]:
                            entities["media_name"] = groups[0].strip()
                    elif intent == "PLAY_SPOTIFY":
                        if len(groups) >= 2 and groups[1]:
                            entities["media_name"] = groups[1].strip()
                        elif len(groups) == 1 and groups[0] and groups[0] not in ["open spotify", "go to spotify"]:
                            entities["media_name"] = groups[0].strip()
                    elif intent in ["OPEN_APP", "CLOSE_APP"]:
                        entities["app_name"] = groups[-1].strip() if groups else ""
                    elif intent == "SYSTEM_CONTROL":
                        entities["action"] = text
                    elif intent == "SEARCH_WEB":
                        entities["query"] = groups[-1].strip() if groups else ""
                    elif intent == "TAKE_NOTE":
                        entities["content"] = groups[-1].strip() if groups else ""
                    elif intent == "WEATHER":
                        entities["city"] = groups[-1].strip() if len(groups) >= 2 and groups[-1] else ""
                    elif intent == "SET_REMINDER":
                        entities["when"] = groups[0].strip() if len(groups) >= 1 else ""
                        entities["message"] = groups[1].strip() if len(groups) >= 2 else ""
                    elif intent == "BRIGHTNESS":
                        entities["direction"] = "up" if "up" in text or "increase" in text or "brighter" in text else "down"
                    elif intent == "WIFI_TOGGLE":
                        entities["state"] = "on" if ("on" in text or "enable" in text) and "off" not in text and "disable" not in text else "off"
                    elif intent == "DESKTOP_CONTROL":
                        entities["action"] = text
                    elif intent == "AUTO_START":
                        entities["enable"] = "disable" not in text and "don't" not in text
                    elif intent == "GAME_UPDATE":
                        platform_match = re.search(r"(steam|epic)", text)
                        entities["platform"] = platform_match.group(1) if platform_match else "steam"
                    elif intent == "CLIPBOARD_TOOL":
                        action_match = re.search(r"(translate|summarize|explain|fix)", text)
                        entities["action"] = action_match.group(1) if action_match else ""
                    elif intent == "CODE_HELPER":
                        entities["request"] = text
                    elif intent == "SEND_MESSAGE":
                        if "telegram" in text:
                            entities["platform"] = "telegram"
                            entities["message"] = groups[-1].strip() if groups else ""
                        else:
                            entities["platform"] = "whatsapp"
                            entities["contact"] = groups[0].strip() if len(groups) >= 1 else ""
                            entities["message"] = groups[1].strip() if len(groups) >= 2 else ""

                    return intent, entities, 0.95

        return "UNKNOWN", {"raw_text": text}, 0.30
