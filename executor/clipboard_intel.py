"""
Clipboard Intelligence - lay noi dung trong clipboard va nho AI Brain
(Claude, qua core/llm.py) de Dich / Tom tat / Giai thich / Sua loi.

Day la mot trong nhung tinh nang "Nhom B": ban than viec doc clipboard
khong can API key, nhung phan xu ly ngon ngu (dich/tom tat/giai thich/sua)
can goi Claude qua LLMBrain da co san trong repo.
"""
try:
    import pyperclip
except ImportError:
    pyperclip = None

_PROMPTS = {
    "translate": "Dich doan van ban sau sang tieng Anh (neu no dang la tieng Viet) hoac sang tieng Viet (neu no dang la tieng Anh). Chi tra ve ban dich, khong giai thich them:\n\n{text}",
    "summarize": "Tom tat doan van ban sau thanh 2-3 cau ngan gon, giu lai y chinh:\n\n{text}",
    "explain": "Giai thich doan van ban / doan code sau mot cach de hieu, ngan gon:\n\n{text}",
    "fix": "Sua loi chinh ta / ngu phap trong doan van ban sau va tra ve ban da sua, khong giai thich them:\n\n{text}",
}


def get_clipboard_text():
    if not pyperclip:
        return None
    try:
        return pyperclip.paste()
    except Exception:
        return None


def process_clipboard(action: str, llm) -> str:
    """action: 'translate' | 'summarize' | 'explain' | 'fix'"""
    if not pyperclip:
        return "Clipboard access is not available. Please install 'pyperclip'."

    text = get_clipboard_text()
    if not text or not text.strip():
        return "Your clipboard is empty, sir."

    if action not in _PROMPTS:
        return "I can translate, summarize, explain, or fix text from your clipboard, sir."

    if not llm or not llm.available:
        return (
            "The AI Brain is offline, sir. Set ANTHROPIC_API_KEY to enable "
            "clipboard translate/summarize/explain/fix."
        )

    prompt = _PROMPTS[action].format(text=text[:4000])  # gioi han do dai de tranh vuot token
    result = llm.ask(prompt)
    if not result:
        return "Sorry sir, I could not process the clipboard content."

    # Ghi de ket qua vao lai clipboard de nguoi dung dan (paste) ngay
    try:
        pyperclip.copy(result)
    except Exception:
        pass

    return f"Done, sir. Result copied back to your clipboard: {result}"
