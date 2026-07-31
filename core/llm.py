"""
Component LLM Brain - "Bo nao AI" that su cua Agent.

Day la phan bien mot chatbot dieu khien bang regex thanh mot AI Voice Agent
thuc su: khi NLU (rule-based) khong nhan dien duoc cau lenh ro rang (intent
UNKNOWN hoac do tin cay thap), thay vi tra loi cau co dinh "toi khong hieu",
Agent se goi Claude (Anthropic API) de HIEU va TRA LOI tu nhien cau hoi tu do
cua nguoi dung, giong nhu mot tro ly AI that su.

Neu chua cai dat package `anthropic` hoac chua cau hinh bien moi truong
ANTHROPIC_API_KEY, module se tu dong "tat" (available = False) va Agent se
quay ve hanh vi cu (cau tra loi co dinh / tim kiem Wikipedia-Google) de
khong lam vo ung dung.
"""
import os

try:
    import anthropic
except ImportError:  # Package chua duoc cai, Agent van chay binh thuong
    anthropic = None


class LLMBrain:
    """Wrapper goi Claude (Anthropic API) de xu ly ngon ngu tu nhien tu do,
    dung lam "bo nao" cho cac cau hoi ma NLU rule-based khong khop duoc."""

    DEFAULT_MODEL = "claude-sonnet-4-6"
    DEFAULT_MAX_TOKENS = 200

    SYSTEM_PROMPT = (
        "Ban la J.A.R.V.I.S, mot AI voice assistant dang tro chuyen bang giong "
        "noi voi nguoi dung. Tra loi that ngan gon (1-3 cau), tu nhien, de doc "
        "thanh tieng (TTS). Khong dung markdown, khong dung dinh dang gach dau "
        "dong, khong dung bang bieu. Khi phu hop, ket thuc cau tra loi bang tu "
        "'sir' theo phong cach lich su, trang trong."
    )

    def __init__(self, model: str = None, max_tokens: int = None):
        self.model = model or self.DEFAULT_MODEL
        self.max_tokens = max_tokens or self.DEFAULT_MAX_TOKENS
        self.client = None

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if anthropic is None:
            print(
                "[LLM]: Package 'anthropic' chua duoc cai. "
                "Chay 'pip install anthropic' de bat tinh nang AI fallback."
            )
        elif not api_key:
            print(
                "[LLM]: Bien moi truong ANTHROPIC_API_KEY chua duoc thiet lap. "
                "AI fallback se bi tat, Agent chi dung cac intent co san."
            )
        else:
            try:
                self.client = anthropic.Anthropic(api_key=api_key)
            except Exception as e:
                print(f"[LLM Init Error]: {e}")
                self.client = None

    @property
    def available(self) -> bool:
        """Cho biet AI fallback co san sang su dung hay khong."""
        return self.client is not None

    def ask(self, user_text: str) -> str:
        """Gui cau hoi tu do den Claude va tra ve cau tra loi phu hop de TTS
        doc len. Tra ve None neu khong the tra loi (de Agent tu fallback)."""
        if not self.available or not user_text:
            return None

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=self.SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_text}],
            )
            text_parts = [
                block.text
                for block in response.content
                if getattr(block, "type", "") == "text"
            ]
            answer = " ".join(text_parts).strip()
            return answer or None
        except Exception as e:
            print(f"[LLM Error]: {e}")
            return None
