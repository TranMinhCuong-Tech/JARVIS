"""
Code Helper - review, giai thich, hoac sinh code bang Claude (qua
core/llm.py). Thuoc "Nhom B": can ANTHROPIC_API_KEY de hoat dong.
"""

_SYSTEM_STYLE_HINT = (
    "Ban dang duoc hoi trong vai tro tro ly lap trinh cua J.A.R.V.I.S. "
    "Tra loi ngan gon, tap trung vao code va giai thich cot loi, phu hop de doc to (TTS) "
    "neu can thiet nhung cung co the chua code block. Request: "
)


def code_helper(request: str, llm) -> str:
    if not request:
        return "Please tell me what code help you need, sir."

    if not llm or not llm.available:
        return (
            "The AI Brain is offline, sir. Set ANTHROPIC_API_KEY to enable "
            "the code helper feature."
        )

    result = llm.ask(_SYSTEM_STYLE_HINT + request)
    if not result:
        return "Sorry sir, I could not process that coding request."
    return result
