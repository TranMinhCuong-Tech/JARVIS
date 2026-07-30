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
            "SEARCH_WEB": [
                r"\b(search\s+for|google|find\s+info\s+about|lookup)\s+(.+)",
                r"\b(what\s+is|who\s+is|tell\s+me\s+about)\s+(.+)"
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
            "IP_ADDRESS": [
                r"\b(what\s+is\s+my\s+ip|my\s+ip\s+address|show\s+my\s+ip|what\'s\s+my\s+ip)\b"
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
            ]
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

                    return intent, entities, 0.95

        return "UNKNOWN", {"raw_text": text}, 0.30
