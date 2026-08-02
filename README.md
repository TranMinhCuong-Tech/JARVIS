# AI Voice Agent - J.A.R.V.I.S

![JARVIS](assets/image.png)

J.A.R.V.I.S is a Python-based voice assistant application that combines a Tkinter interface with a 3D particle sphere, speech recognition (ASR), natural language understanding (NLU), text-to-speech (TTS), and system automation such as opening applications, controlling volume, searching the web, sending messages, and monitoring the system.

This project is designed in a modular way, making it easy to extend and suitable for learning about AI agent architecture, natural language processing, action planning, and UI integration.

## 1. Project Overview

J.A.R.V.I.S is more than a simple voice command bot. It has two main processing layers:

- The first layer is rule-based NLU, which is fast and reliable for clearly defined commands such as opening Notepad, increasing volume, taking screenshots, asking for the time, or closing an app.
- The second layer is the AI Brain, powered by Anthropic Claude, which handles more open-ended user requests that do not match predefined intents. If no API key is configured, the system still runs normally and falls back to traditional behavior such as Wikipedia, Google search, or default responses.

This is what makes the project feel like an agent rather than just a static voice-command switchboard.

## 2. System Architecture

```text
ASR -> NLU -> Context Memory -> Decision Engine -> Action Executor -> TTS
                     |
                     v
              AI Brain (Claude / Anthropic)
```

### What each component does

- ASR: captures speech and converts it into text.
- NLU: analyzes the user input, identifies the intent, and extracts entities.
- Context Memory: stores short-term context so the agent can better understand related follow-up requests.
- Decision Engine: selects the appropriate action for each intent.
- Action Executor: performs system operations such as opening browsers, controlling Windows, searching the web, and sending messages.
- TTS: reads the response aloud using speech synthesis.

## 3. Available Features

### 3.1 Core Features (No API key required)

| Feature | Description | Example |
|---|---|---|
| Voice Recognition | Listens to the microphone and turns speech into commands | “Open Notepad” |
| 3D GUI | A particle sphere with animated listening / processing / speaking states | No manual action needed |
| Open / Close Applications | Opens or closes Windows applications | “Open Chrome”, “Close Notepad” |
| System Control | Increases/decreases volume, mutes audio, captures screenshots | “Volume up”, “Take screenshot” |
| Web Search | Uses Wikipedia first and falls back to Google if needed | “Tell me about Python” |
| Note Taking | Saves notes to a file on the Desktop | “Take a note buy milk tomorrow” |
| Time / Date | Answers with the current time or date | “What time is it” |
| IP Address | Retrieves the machine IP using Python’s built-in socket module | “What is my IP” |
| Lock Computer | Locks the Windows workstation | “Lock computer” |
| Shutdown | Shuts down the computer after 5 seconds | “Shutdown computer” |
| Sleep Mode | Puts the computer to sleep | “Sleep” |
| Exit | Stops the agent using commands such as bye / stop / exit | “Bye” |

### 3.2 Extended Features (No API key required)

| Feature | Description | Example |
|---|---|---|
| Weather | Retrieves free weather data from Open-Meteo | “What’s the weather in Hanoi” |
| System Monitoring | Checks CPU, RAM, Disk, and GPU usage | “Check CPU”, “System stats” |
| Reminder | Sets reminders with desktop notifications | “Remind me in 10 minutes to call John” |
| Brightness Control | Increases or decreases screen brightness | “Brightness up” |
| Wi-Fi Toggle | Turns Wi-Fi on/off on Windows using netsh | “Turn off wifi” |
| Desktop Control | Minimizes windows, switches windows, or shows the desktop | “Show desktop” |
| Auto-start on Boot | Registers the app to launch automatically at startup | “Start with Windows” |
| Game Update | Opens Steam/Epic to trigger update checks | “Update my games on steam” |
| WhatsApp Messaging | Opens WhatsApp Web and pre-fills a message | “Send whatsapp message to mom saying I’ll be late” |
| Telegram Messaging | Opens Telegram Web with a pre-filled message | “Send telegram message saying on my way” |

### 3.3 Features Requiring ANTHROPIC_API_KEY

| Feature | Description | Example |
|---|---|---|
| Clipboard Intelligence | Translates, summarizes, explains, or fixes the current clipboard content | “Translate my clipboard” |
| Code Helper | Asks Claude to write, review, or explain code | “Help me code a bubble sort in Python” |

> These two features reuse the same ANTHROPIC_API_KEY used by the AI Brain, so no separate key is required.

## 4. Project Structure

```text
JarvisFull/
├── agent/
│   └── decision_engine.py
├── assets/
├── core/
│   ├── asr.py
│   ├── context.py
│   ├── llm.py
│   └── tts.py
├── executor/
│   ├── actions.py
│   ├── auto_start.py
│   ├── clipboard_intel.py
│   ├── code_helper.py
│   ├── contacts.json
│   ├── desktop_control.py
│   ├── game_updater.py
│   ├── reminder.py
│   ├── send_message.py
│   ├── system_monitor.py
│   └── weather.py
├── nlu/
│   └── intent_parser.py
├── gui.py
├── main.py
├── README.md
└── requirements.txt
```

## 5. File Roles

- main.py: application entry point; initializes modules and starts the command loop.
- gui.py: main Tkinter interface with the 3D sphere, status area, and text input box.
- agent/decision_engine.py: main planner that decides which action should be triggered for each intent.
- nlu/intent_parser.py: classifies intents and extracts entities from user input using regex patterns.
- core/asr.py: handles speech recognition.
- core/context.py: stores short-term conversational context.
- core/llm.py: wrapper for Claude via Anthropic API for free-form questions.
- core/tts.py: converts text responses into speech.
- executor/actions.py: core actions such as opening YouTube, Spotify, apps, notes, and network-related behavior.
- executor/weather.py: fetches weather information from Open-Meteo.
- executor/system_monitor.py: reads CPU, RAM, Disk, and GPU information.
- executor/reminder.py: handles reminder notifications.
- executor/desktop_control.py: manages brightness, Wi-Fi, and basic desktop actions.
- executor/auto_start.py: enables startup automation.
- executor/send_message.py: opens WhatsApp or Telegram for message sending.

## 6. System Requirements

### 6.1 Operating System
- Windows 10/11 is the primary target platform.
- Some features can also work on macOS/Linux, but Windows is best for app automation, Wi-Fi control, and app launching behavior.

### 6.2 Python
- Python 3.12 is recommended.
- Python 3.10 or 3.11 may also work, but 3.12 is the best choice.

### 6.3 Input Devices
- A microphone is required for voice interaction.
- If the microphone is unavailable, you can still type commands manually into the text input field.

## 7. Windows Installation Guide

### Step 1: Install Python
Open PowerShell as Administrator and run:

```powershell
winget install Python.Python.3.12
```

Verify the installation:

```powershell
python --version
```

If Python is not recognized, add it to PATH manually.

### Step 2: Download or Extract the Project
Example:

```powershell
cd D:\JarvisFull
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

### Step 5: Install Dependencies

```powershell
pip install -r requirements.txt
```

### Step 6: If pyaudio fails to install
On Windows, pyaudio may require a separate wheel. If installation fails, download the correct wheel from the Gohlke repository and install it manually:

```powershell
pip install PyAudio-0.2.14-cp312-cp312-win_amd64.whl
```

### Step 7 (Optional): Enable the AI Brain
To allow the agent to answer free-form questions with Claude, set the environment variable:

```powershell
$env:ANTHROPIC_API_KEY = "your-api-key-here"
```

If this is not configured, the app will still run, but the AI Brain will remain offline and use standard fallbacks.

## 8. Running the Application

With the virtual environment activated:

```powershell
python main.py
```

When it starts, the 3D interface will open and the agent will greet you based on the time of day.

## 9. Useful Example Commands

### Opening Applications
- “Open Notepad”
- “Open Chrome”
- “Launch Spotify”

### Playing Music
- “Play Starboy on YouTube”
- “Play Blinding Lights on Spotify”

### System Control
- “Volume up”
- “Mute”
- “Take screenshot”

### Search and Information
- “What time is it”
- “What day is today”
- “What is my IP”
- “Tell me about Python”

### New Features
- “What’s the weather in Hanoi”
- “Remind me in 10 minutes to call John”
- “Brightness up”
- “Turn off wifi”
- “Show desktop”
- “Send whatsapp message to mom saying I’ll be late”

## 10. Important Notes

- The project is primarily optimized for English voice commands.
- Some features such as app launching, Windows control, Wi-Fi toggle, and messaging work best on Windows.
- WhatsApp requires the user to be logged into WhatsApp Web in the default browser before messaging can work.
- If you use the AI Brain, make sure the terminal session where you run the app also has the ANTHROPIC_API_KEY variable assigned.
- Some automation features may require Administrator privileges or appropriate system access.

## 11. Troubleshooting

| Issue | Solution |
|---|---|
| Module not found | Run `pip install -r requirements.txt` inside the virtual environment |
| pyaudio installation fails | Download the correct Windows wheel or use a compatible Python version |
| Microphone not detected | Check microphone access permissions in Windows Settings |
| TTS does not speak | Make sure a default speech voice is installed on Windows |
| AI Brain does not respond | Check ANTHROPIC_API_KEY and confirm that the terminal session is the same one used to launch the app |
| Commands repeat | The system includes anti-echo / duplicate filtering, but using the latest version is recommended |

## 12. Current Limitations

This project is currently more of an educational and experimental AI assistant than a full commercial voice assistant. Some limitations include:

- NLU is still based on regex patterns, so it works best for clear commands rather than complex conversational dialogue.
- Some automation features that interact with UI elements may require a desktop environment and compatible mouse/keyboard behavior.
- The AI Brain is currently turn-based rather than a continuous live stream like Gemini Live.

## 13. License

This project is intended for learning, experimentation, and personal use. Feel free to modify and extend it further.

## 14. Notes for Developers

If you want to improve the project, the next priorities could be:

- expanding the NLU with more command patterns and better Vietnamese support,
- adding longer-term memory and conversation history,
- improving error handling and logging,
- integrating more advanced AI vision or web browsing capabilities.
