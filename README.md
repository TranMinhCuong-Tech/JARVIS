# JARVIS Local Assistant

![JARVIS HUD](assets/image.png)

JARVIS is a local-first desktop assistant inspired by Iron Man's AI. It runs on your computer without requiring cloud APIs or external AI model keys. The project uses local command parsing, voice recognition, desktop automation, and optional text-to-speech for a more interactive, movie-style experience — now with a cinematic animated HUD and a wider set of built-in skills.

## Project Idea

The goal of this project is to create a lightweight JARVIS-style assistant that can:
- listen for voice commands,
- execute desktop actions,
- open apps and web pages,
- control media playback,
- send messages,
- check the weather, do quick math, take notes, and set reminders,
- respond with voice or text,
- and remember simple preferences.

This is not a full cloud-powered chatbot. Instead, it is a rule-driven local assistant built for easy extension and offline-friendly workflows.

## Supported Platforms

- Windows 10/11
- macOS 12+
- Linux (any distro with a desktop session, e.g. Ubuntu, Fedora, Arch)

## Requirements

- Python 3.10 or newer (tested up to 3.14)
- `Tkinter` for the desktop UI
- `SpeechRecognition` for voice input (uses `sounddevice` for microphone capture by default — no `PyAudio` needed)
- `pyttsx3` for optional local text-to-speech
- `psutil` for live CPU / RAM / battery readouts in the HUD

All Python dependencies are listed in `requirements.txt`, including platform-specific markers so a single `pip install -r requirements.txt` works correctly on Windows, macOS, and Linux — **without needing to compile anything**.

> **Note on PyAudio:** `requirements.txt` intentionally does *not* install `PyAudio`. It is a native extension that often fails to build on Windows (missing `portaudio.h` / Visual C++ headers) and on very new Python versions like 3.14 that don't have prebuilt wheels yet. JARVIS doesn't need it: `SpeechRecognition` automatically records through `sounddevice` (already included) when `PyAudio` isn't present. If you want to install `PyAudio` anyway, see the bottom of `requirements.txt` for OS-specific instructions.

## Installation

1. Install Python 3.10+ from [python.org](https://www.python.org/downloads/) (make sure to check "Add to PATH" on Windows).

2. **Linux only** — install the system package needed by Tkinter first (audio works out of the box via `sounddevice`, no extra system packages required):
```bash
# Debian/Ubuntu
sudo apt-get update
sudo apt-get install -y python3-tk

# Fedora
sudo dnf install -y python3-tkinter

# Arch
sudo pacman -S tk
```

3. Create and activate a virtual environment.

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

4. Run the application:
```bash
python main.py
```

## Features

### Cinematic animated HUD
- Boot-up sequence with a typed status log, just like an AI core coming online.
- Circular arc-reactor style HUD with layered glow rings, a rotating radar sweep, drifting particles, and a live voice waveform while JARVIS speaks.
- Corner brackets and a sci-fi grid background for a true movie-console feel.
- Live top-left SYSTEM panel (CPU / RAM / battery bars) and top-right TIME panel (clock + date), refreshed every second.
- Color-coded state ring: cyan idle, green listening, amber thinking, cyan-white executing, pink speaking, red error.
- Colorized conversation log (You / JARVIS / System) with timestamps.
- One-click MIC and VOICE toggle buttons in the command bar.

### Core assistant
- Automatic voice listening after startup, with manual mic toggle.
- Voice recognition using `SpeechRecognition`; falls back to `sounddevice` when needed.
- Text-to-speech output with `pyttsx3` when available, with a mute toggle.
- Open and close applications by name, cross-platform.
- Play music on Spotify; search or auto-play the first result on YouTube in the default or a named browser.
- Send messages on WhatsApp and other messaging platforms.
- Lock, sleep, or shut down the computer — always with a spoken confirmation step.
- Open the webcam / camera viewer.
- Remember simple free-form preferences ("remember that my favorite color is blue") and recall them later.

### New skills
- **Weather** — "what's the weather" or "weather in Tokyo" (free, keyless Open-Meteo API, IP-based location fallback).
- **Jokes & quotes** — "tell me a joke", "inspire me".
- **Calculator** — "calculate 12 times 8 plus 5", "what is 45 divided by 9" (safe AST-based parser, no `eval`).
- **Notes** — "take a note buy milk", "read my notes", "clear my notes".
- **Reminders & timers** — "remind me in 10 minutes to check the oven", "set a timer for 5 minutes".
- **Screenshots** — "take a screenshot" (saved to `~/Pictures/JARVIS_Screenshots`).
- **Media control** — "play music", "pause music", "next song", "volume up", "mute".
- **Translation** — "translate hello to spanish" (via `deep-translator`).
- **Google search** — "search google for best pizza in Rome".
- **Battery & system status** — "system status", "battery level".
- **Wikipedia & public IP** lookups, as before.

## Example Commands

- `open spotify`
- `play Shape of You on Spotify`
- `open Despacito on YouTube in Edge`
- `what's the weather in Paris`
- `tell me a joke`
- `calculate 25 percent of 480` *(spoken as `calculate 480 times 0.25`)*
- `take a note call mom tomorrow`
- `remind me in 15 minutes to stretch`
- `take a screenshot`
- `translate good morning to french`
- `search google for best pizza in rome`
- `send message to Minh on WhatsApp`
- `close chrome`
- `system status`
- `what time is it`
- `bye`

## How to Use

- Start the app with `python main.py`.
- Watch the boot sequence, then speak a command or type it into the input box.
- Use the `SEND` button or press `Enter` to submit text.
- Use `MIC: ON/OFF` to pause automatic voice listening, and `VOICE: ON/OFF` to mute spoken replies while keeping the text log.
- The assistant responds in the HUD log and speaks back if `pyttsx3` is installed and voice output is enabled.
- Say `bye`, `goodbye`, or `you can sleep` to stop the assistant.

## Notes

- Command understanding is local and rule-based, not powered by a cloud LLM — fast, private, and works offline for most actions.
- Voice recognition can use Google Web Speech without an API key, but it requires internet access. If `pocketsphinx` is installed, offline recognition may be available.
- Weather, translation, Wikipedia, IP lookup, and Google search need an internet connection; everything else works fully offline.
- For best desktop automation with Spotify and messaging apps, keep `pyautogui` and `pyperclip` installed.

## Project Structure

- `main.py` — application entry point.
- `jarvis/app.py` — starts the UI.
- `jarvis/ui.py` — the animated Tkinter HUD (boot sequence, HUD rendering, status panels, event loop).
- `jarvis/command_router.py` — local command parsing and feature dispatch.
- `jarvis/speech.py` — voice recognition and text-to-speech.
- `jarvis/automation.py` — Spotify, YouTube, WhatsApp, and browser automation.
- `jarvis/app_launcher.py` — cross-platform app open/close logic.
- `jarvis/power_control.py` — lock / sleep / shutdown.
- `jarvis/camera.py` — webcam viewer.
- `jarvis/system_info.py` — time, date, CPU/RAM/battery status.
- `jarvis/weather.py` — keyless weather lookups.
- `jarvis/calculator.py` — safe arithmetic parsing.
- `jarvis/fun.py` — jokes and quotes.
- `jarvis/screenshot.py` — screen capture.
- `jarvis/media_control.py` — media key control (play/pause/volume/track).
- `jarvis/translator.py` — text translation.
- `jarvis/reminders.py` — background timers/reminders.
- `jarvis/user_memory.py` — local JSON store for preferences, history, and notes.
- `requirements.txt` — Python dependency list with per-OS markers.
