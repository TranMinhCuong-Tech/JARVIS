from __future__ import annotations


def public_ip_address() -> str:
    """Return the machine's public IP address using a simple HTTPS endpoint."""
    try:
        import requests

        response = requests.get("https://api.ipify.org", timeout=8)
        response.raise_for_status()
        ip = response.text.strip()
        if not ip:
            return "I could not find your public IP address, sir."
        return f"Your IP address is {ip}, sir."
    except Exception as exc:
        return f"I could not get your IP address, sir. Details: {exc}"


def wikipedia_summary(topic: str, sentences: int = 2) -> str:
    """Search Wikipedia and return a short spoken-friendly summary."""
    topic = topic.strip()
    if not topic:
        return "Please tell me what you want me to search on Wikipedia, sir."

    try:
        import wikipedia

        wikipedia.set_lang("en")
        try:
            summary = wikipedia.summary(topic, sentences=sentences, auto_suggest=True)
            return f"According to Wikipedia, {summary}"
        except wikipedia.exceptions.DisambiguationError as exc:
            options = ", ".join(exc.options[:5])
            return f"Wikipedia found multiple results for {topic}, sir. Please be more specific. Options include: {options}."
        except wikipedia.exceptions.PageError:
            results = wikipedia.search(topic, results=1)
            if not results:
                return f"I could not find anything about {topic} on Wikipedia, sir."
            summary = wikipedia.summary(results[0], sentences=sentences, auto_suggest=False)
            return f"According to Wikipedia, {summary}"
    except Exception as exc:
        return f"I could not search Wikipedia, sir. Details: {exc}"
