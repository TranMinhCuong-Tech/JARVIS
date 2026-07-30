from typing import Optional

class ContextMemory:
    """
    Component Context Memory - Luu tru va giai quyet ngu canh hoi thoai.
    """
    def __init__(self):
        self.last_intent: Optional[str] = None
        self.last_target: Optional[str] = None
        self.last_action_success: bool = False
        self.history = []

    def update(self, intent: str, target: Optional[str], success: bool = True):
        self.last_intent = intent
        if target:
            self.last_target = target
        self.last_action_success = success
        self.history.append({"intent": intent, "target": target, "success": success})

    def resolve_target(self, current_target: Optional[str]) -> Optional[str]:
        if current_target in ["it", "that", "this", "song", "video", "app", "no"]:
            return self.last_target
        return current_target
