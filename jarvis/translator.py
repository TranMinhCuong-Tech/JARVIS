from __future__ import annotations

_LANGUAGE_CODES = {
    "english": "en",
    "vietnamese": "vi",
    "spanish": "es",
    "french": "fr",
    "german": "de",
    "japanese": "ja",
    "korean": "ko",
    "chinese": "zh-CN",
    "russian": "ru",
    "portuguese": "pt",
    "italian": "it",
    "thai": "th",
}


def translate_text(text: str, target_language: str) -> str:
    """Translate text to the requested language using deep-translator (free, keyless)."""
    text = text.strip()
    if not text:
        return "Please tell me what you want me to translate, sir."

    target = _LANGUAGE_CODES.get(target_language.strip().lower(), target_language.strip().lower())

    try:
        from deep_translator import GoogleTranslator

        result = GoogleTranslator(source="auto", target=target).translate(text)
        return f"In {target_language}, that is: {result}"
    except Exception as exc:
        return f"I could not translate that, sir. Please install deep-translator. Details: {exc}"
