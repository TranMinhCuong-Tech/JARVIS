# AI Voice Agent - J.A.R.V.I.S

A modular AI Voice Agent built with Python and Tkinter, featuring a 3D particle sphere interface, speech recognition (ASR), natural language understanding (NLU), and text-to-speech (TTS).

## Architecture

```
ASR -> NLU (Intent + Entity) -> Context Memory -> Decision Engine -> Action Executor -> TTS
```

## Features

| Feature | Description |
|---------|-------------|
| **Voice Recognition** | Continuous microphone listening with English & Vietnamese support |
| **3D Sphere GUI** | Particle sphere with perspective rotation, glow effects, and audio-reactive distortion |
| **YouTube Playback** | Search and play videos directly in browser |
| **Spotify Control** | Open Spotify, search songs, and auto-click play |
| **App Management** | Open and close applications via Windows Start menu / taskkill |
| **System Control** | Volume up/down/mute, take screenshots |
| **Web Search** | Wikipedia summary or Google search fallback |
| **Note Taking** | Save quick notes to `jarvis_notes.txt` on Desktop |
| **Time & Date** | Ask "what time is it" or "what day is today" |
| **IP Address** | Reports both local (via Python `socket`) and public IP |
| **Lock Screen** | Lock your Windows workstation |
| **Shutdown** | Shutdown your computer after a 5-second countdown |
| **Sleep Mode** | Put your computer to sleep |
| **Exit** | Say "bye", "stop", or "exit" to close the agent |

## Project Structure

```
AI_voice_agent_project/
├── agent/
│   ├── __init__.py
│   └── decision_engine.py      # Intent routing & action planning
├── core/
│   ├── __init__.py
│   ├── asr.py                  # Speech Recognition (SpeechRecognition)
│   ├── context.py              # Conversation context memory
│   └── tts.py                  # Text-to-Speech (pyttsx3)
├── executor/
│   ├── __init__.py
│   └── actions.py              # System actions (browser, apps, volume, etc.)
├── nlu/
│   ├── __init__.py
│   └── intent_parser.py        # Regex-based intent & entity extraction
├── gui.py                      # Tkinter 3D particle sphere interface
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
└── REAME.md                    # This file
```

## Prerequisites

- **OS**: Windows 10 / 11
- **Python**: 3.12 (recommended)
- **Microphone**: Required for voice input (text input works as fallback)

## Installation

### Step 1: Install Python 3.12 via Winget

Open PowerShell as Administrator and run:

```powershell
winget install Python.Python.3.12
```

After installation, verify Python is added to PATH:

```powershell
python --version
# Should print: Python 3.12.x
```

If `python` is not recognized, add it manually:
- Default install path: `C:\Users\<YourUser>\AppData\Local\Programs\Python\Python312`
- Add both `Python312` and `Python312\Scripts` to your System Environment Variables -> PATH.

### Step 2: Clone or Extract the Project

Extract the ZIP file to a folder, e.g.:

```powershell
cd D:\AI_voice_agent_project
```

### Step 3: Create a Virtual Environment

```powershell
py -3.12 -m venv .venv
```

### Step 4: Activate the Virtual Environment

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.venv\Scripts\Activate.ps1
```

Your prompt should now show `(.venv)` at the beginning.

### Step 5: Install Dependencies

```powershell
pip install -r requirements.txt
```

> **Note**: `pyaudio` may require a pre-built wheel on Windows. If `pip install pyaudio` fails, download the appropriate wheel from [https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) and install it:
> ```powershell
> pip install PyAudio-0.2.14-cp312-cp312-win_amd64.whl
> ```

## Running the Application

With the virtual environment activated:

```powershell
python main.py
```

The GUI will open with a 3D particle sphere. The agent will greet you based on the time of day:

- **Morning** (00:00 - 11:59): *"Good morning, sir. Please tell me how can I help you, sir?"*
- **Afternoon** (12:00 - 17:59): *"Good afternoon, sir..."*
- **Evening** (18:00 - 23:59): *"Good evening, sir..."*

## Test Cases

### 1. Play Music on YouTube
**Say:** *"Play Starboy on YouTube"*

**Expected:** Browser opens YouTube with the song playing.

### 2. Play Music on Spotify
**Say:** *"Play Blinding Lights on Spotify"*

**Expected:** Spotify opens, searches for the song, and clicks play.

### 3. Open an Application
**Say:** *"Open Notepad"*

**Expected:** Windows Start menu opens, types "Notepad", and launches it.

### 4. Close an Application
**Say:** *"Close Notepad"*

**Expected:** Notepad process is terminated.

### 5. Volume Control
**Say:** *"Volume up"*

**Expected:** System volume increases by 5 steps. Agent responds: *"Volume increased, sir."*

### 6. Take a Screenshot
**Say:** *"Take screenshot"*

**Expected:** Screenshot saved to `C:\Users\<You>\Pictures\screenshot_<timestamp>.png`.

### 7. Ask for Time
**Say:** *"What time is it"*

**Expected:** Agent responds with the current time, e.g. *"The current time is 02:15 PM, sir."*

### 8. Ask for Date
**Say:** *"What day is today"*

**Expected:** Agent responds with the current date, e.g. *"Today is Thursday, July 31, 2026, sir."*

### 9. Ask for IP Address
**Say:** *"What is my IP"*

**Expected:** Agent reports both local and public IP addresses.

### 10. Lock Computer
**Say:** *"Lock computer"*

**Expected:** Windows workstation locks immediately.

### 11. Shutdown Computer
**Say:** *"Shutdown computer"*

**Expected:** Agent confirms, then system shuts down after 5 seconds.

### 12. Put Computer to Sleep
**Say:** *"Sleep"*

**Expected:** Computer enters sleep mode.

### 13. Take a Note
**Say:** *"Take a note buy milk tomorrow"*

**Expected:** Note appended to `jarvis_notes.txt` on Desktop.

### 14. Exit the Agent
**Say:** *"Bye"* or *"Stop"*

**Expected:** Agent says goodbye and the application closes after 2 seconds.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `No module named 'speech_recognition'` | Run `pip install SpeechRecognition` inside the venv |
| `pyaudio` install fails | Download pre-built wheel from [Christoph Gohlke's site](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) |
| Microphone not detected | Check Windows Privacy Settings -> Microphone access is allowed for apps |
| Commands repeat in a loop | This is fixed by anti-echo filtering. Ensure you are using the latest version of `main.py` |
| TTS not speaking | Ensure you have a default Windows voice installed (Settings -> Time & Language -> Speech) |

## License

Personal use only. Built for educational and productivity purposes.
