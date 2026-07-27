# JARVIS Local Assistant

![JARVIS HUD](assets/image.png)

JARVIS is a local-first desktop assistant inspired by Iron Man's AI. It runs on your computer without requiring cloud APIs or external AI model keys. The project uses local command parsing, voice recognition, desktop automation, and optional text-to-speech for a more interactive experience.

## Project Idea

The goal of this project is to create a lightweight JARVIS-style assistant that can:
- listen for voice commands,
- execute desktop actions,
- open apps and web pages,
- control media playback,
- send messages,
- respond with voice or text,
- and remember simple preferences.

This is not a full cloud-powered chatbot. Instead, it is a rule-driven local assistant built for easy extension and offline-friendly workflows.

## Supported Platforms

- Windows
- macOS
- Linux

## Requirements

- Python 3.14 or newer
- `Tkinter` for the desktop UI
- `SpeechRecognition` for voice input
- `sounddevice` for microphone recording fallback
- `pyttsx3` for optional local text-to-speech

Dependencies are listed in `requirements.txt`.

## Installation

1. Create and activate a virtual environment.

Windows:
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Install additional packages as needed:
- `pyttsx3` for voice output
- `pyautogui` and `pyperclip` for desktop automation in apps like Spotify and WhatsApp

## Run the Application

```bash
python main.py
```

## Features

- Minimal Tkinter desktop UI with a JARVIS-style animated HUD and text command input.
- Automatic voice listening after startup.
- Voice recognition using `SpeechRecognition`; falls back to `sounddevice` when needed.
- Text-to-speech output with `pyttsx3` when available.
- Open and close applications.
- Play music on Spotify.
- Search or play videos on YouTube using the default browser or a named browser.
- Send messages on WhatsApp and other messaging platforms.
- Show system time, date, and status information.
- Lock, sleep, or shut down the computer with confirmation.
- Open the webcam or camera application.
- Remember simple user preferences and recall them later.

## Example Commands

- `open spotify`
- `play Shape of You on Spotify`
- `open Despacito on YouTube in Edge`
- `play starboy song on youtube`
- `send message to Minh on WhatsApp`
- `close chrome`
- `system status`
- `what time is it`
- `what is day today`
- `bye`

## How to Use

- Start the app with `python main.py`.
- Speak a command or type it into the input box.
- Use the `SEND` button or press `Enter` to submit text.
- The assistant will respond in the UI and optionally speak back if `pyttsx3` is installed.
- Say `bye`, `goodbye`, or `you can sleep` to stop the assistant.

## Notes

- Command understanding is local and rule-based, not powered by a cloud LLM.
- Voice recognition can use Google Web Speech without an API key, but it requires internet access.
- If `pocketsphinx` is installed, offline speech recognition may be available.
- For best automation with Spotify and messaging apps, install `pyautogui` and `pyperclip`.

## Project Structure

- `main.py` — application entry point.
- `jarvis/app.py` — starts the UI.
- `jarvis/command_router.py` — local command parsing and logic.
- `jarvis/ui.py` — Tkinter user interface.
- `jarvis/speech.py` — voice recognition and text-to-speech.
- `jarvis/automation.py` — Spotify, YouTube, WhatsApp, and browser automation.
- `requirements.txt` — Python dependency list.
