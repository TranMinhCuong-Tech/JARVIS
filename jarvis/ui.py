from __future__ import annotations

import math
import queue
import random
import threading
import time
import tkinter as tk
from tkinter import ttk

from .command_router import CommandRouter
from .speech import VoiceRecognizer, speak
from .system_info import day_period
from .user_memory import UserMemory


class JarvisUI:
    """Minimal animated circular JARVIS HUD."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("JARVIS")
        self.root.geometry("1024x640")
        self.root.minsize(820, 520)
        self.root.configure(bg="#071722")

        self.router = CommandRouter()
        self.memory = UserMemory()
        self.voice = VoiceRecognizer()
        self.events: queue.Queue[tuple[str, str]] = queue.Queue()
        self.is_listening = False
        self.auto_voice = True
        self.ui_state = "idle"
        self.history = self.memory.command_history()
        self.history_index = len(self.history)
        self.suggestion_var = tk.StringVar(value="try: play Starboy song on spotify")
        self._phase = 0.0
        self._dust = [
            (random.random() * math.tau, random.uniform(0.35, 1.08), random.uniform(0.4, 1.8))
            for _ in range(90)
        ]

        self._setup_style()
        self._build_layout()
        self._say(self._startup_greeting())
        self._animate()
        self._drain_events()
        self.root.after(900, self.listen_voice)

    def run(self) -> None:
        self.root.mainloop()

    def _startup_greeting(self) -> str:
        period = day_period()
        return f"Good {period}, sir. How can I help you today, sir?"

    def _setup_style(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Jarvis.TButton", background="#0a2530", foreground="#9fffff", borderwidth=1, padding=(12, 8))
        style.map("Jarvis.TButton", background=[("active", "#104153")])

    def _build_layout(self) -> None:
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_columnconfigure(0, weight=1)

        self.hud = tk.Canvas(self.root, bg="#071722", highlightthickness=0)
        self.hud.grid(row=0, column=0, sticky="nsew")

        command = tk.Frame(self.root, bg="#071722")
        command.grid(row=1, column=0, sticky="ew", padx=34, pady=(0, 24))
        command.grid_columnconfigure(0, weight=1)

        self.input_var = tk.StringVar()
        entry = tk.Entry(
            command,
            textvariable=self.input_var,
            bg="#08131a",
            fg="#d7fbff",
            insertbackground="#52ffff",
            relief="flat",
            font=("Consolas", 12),
        )
        entry.grid(row=0, column=0, sticky="ew", padx=(0, 10), ipady=9)
        entry.bind("<Return>", lambda _event: self._submit_text())
        entry.bind("<Up>", self._history_previous)
        entry.bind("<Down>", self._history_next)
        ttk.Button(command, text="SEND", style="Jarvis.TButton", command=self._submit_text).grid(row=0, column=1)
        tk.Label(
            command,
            textvariable=self.suggestion_var,
            bg="#071722",
            fg="#5cb8c4",
            font=("Consolas", 9),
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", pady=(7, 0))

        self.log = tk.Text(
            self.hud,
            bg="#061018",
            fg="#c3fbff",
            insertbackground="#52ffff",
            relief="flat",
            wrap="word",
            font=("Consolas", 9),
            padx=12,
            pady=8,
            borderwidth=0,
        )
        self.log_window = self.hud.create_window(0, 0, window=self.log, anchor="nw")

    def _animate(self) -> None:
        self._phase += 0.024
        self.hud.delete("hud")
        width = max(self.hud.winfo_width(), 820)
        height = max(self.hud.winfo_height(), 460)
        cx, cy = width / 2, height * 0.45
        r = min(width, height) * 0.25

        self._draw_background(width, height)
        self._draw_circular_hud(cx, cy, r)
        self._position_log(width, height)

        self.root.after(33, self._animate)

    def _draw_background(self, width: int, height: int) -> None:
        for x in range(0, width, 64):
            self.hud.create_line(x, 0, x, height, fill="#09202c", tags="hud")
        for y in range(0, height, 64):
            self.hud.create_line(0, y, width, y, fill="#09202c", tags="hud")

    def _draw_circular_hud(self, cx: float, cy: float, r: float) -> None:
        palette = {
            "idle": ("#55f6ff", "#1b8090", "#9ffcff", 1.0),
            "listening": ("#7dffb0", "#228f67", "#c4ffd9", 1.08),
            "thinking": ("#ffd45c", "#96772c", "#fff0b0", 1.14),
            "executing": ("#55f6ff", "#1b8090", "#ffffff", 1.18),
            "speaking": ("#ff6fd8", "#8c3278", "#ffd2f3", 1.1),
            "error": ("#ff566a", "#8d2632", "#ffd0d5", 1.05),
        }
        cyan, dim, pale, pulse_scale = palette.get(self.ui_state, palette["idle"])
        state_pulse = 1.0 + 0.035 * pulse_scale * math.sin(self._phase * 5)

        for radius, width, color in (
            (r * 1.45 * state_pulse, 2, dim),
            (r * 1.28, 1, cyan),
            (r * 1.08 * state_pulse, 2, dim),
            (r * 0.86, 1, cyan),
            (r * 0.62 * state_pulse, 3, cyan),
        ):
            self.hud.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, outline=color, width=width, tags="hud")

        self._segments(cx, cy, r * 1.45, 13, self._phase * 0.8, cyan, 5, 0.42)
        self._segments(cx, cy, r * 1.26, 18, -self._phase * 1.2, "#3cecff", 3, 0.32)
        self._segments(cx, cy, r * 1.02, 44, self._phase * 1.7, dim, 2, 0.5)
        self._segments(cx, cy, r * 0.78, 72, -self._phase * 2.1, pale, 1, 0.35)
        self._segments(cx, cy, r * 0.64, 3, self._phase * 2.5, cyan, 6, 0.18)

        for index in range(86):
            a = index * math.tau / 86 + self._phase * 0.25
            inner = r * 0.93
            outer = r * (0.99 if index % 5 else 1.07)
            color = cyan if index % 5 == 0 else dim
            self.hud.create_line(
                cx + math.cos(a) * inner,
                cy + math.sin(a) * inner,
                cx + math.cos(a) * outer,
                cy + math.sin(a) * outer,
                fill=color,
                width=1,
                tags="hud",
            )

        for angle, radius, size in self._dust:
            a = angle - self._phase * 0.8
            pulse = 0.55 + 0.45 * math.sin(self._phase * 3 + angle)
            x = cx + math.cos(a) * r * radius
            y = cy + math.sin(a) * r * radius
            dot = size * pulse
            self.hud.create_oval(x - dot, y - dot, x + dot, y + dot, fill="#7cffff", outline="", tags="hud")

        core = r * 0.5
        self.hud.create_oval(cx - core, cy - core, cx + core, cy + core, fill="#092331", outline=cyan, width=3, tags="hud")
        self.hud.create_oval(cx - core * 0.78, cy - core * 0.78, cx + core * 0.78, cy + core * 0.78, outline="#113a48", width=2, tags="hud")
        self.hud.create_text(cx, cy - 2, text="J.A.R.V.I.S", fill="#bafcff", font=("Consolas", 14, "bold"), tags="hud")
        self.hud.create_text(cx, cy + 22, text=self.ui_state.upper(), fill=pale, font=("Consolas", 8), tags="hud")

    def _segments(
        self,
        cx: float,
        cy: float,
        radius: float,
        count: int,
        offset: float,
        color: str,
        width: int,
        fill_ratio: float,
    ) -> None:
        for index in range(count):
            if index % 4 == 2:
                continue
            start = offset + index * math.tau / count
            extent = math.tau / count * fill_ratio
            self.hud.create_arc(
                cx - radius,
                cy - radius,
                cx + radius,
                cy + radius,
                start=math.degrees(start),
                extent=math.degrees(extent),
                style="arc",
                outline=color,
                width=width,
                tags="hud",
            )

    def _position_log(self, width: int, height: int) -> None:
        log_w = int(min(560, width * 0.62))
        log_h = 88
        x = int((width - log_w) / 2)
        y = int(height - log_h - 18)
        self.hud.coords(self.log_window, x, y)
        self.hud.itemconfigure(self.log_window, width=log_w, height=log_h)

    def _submit_text(self, value: str | None = None) -> None:
        text = value or self.input_var.get().strip()
        self.input_var.set("")
        if not text:
            return
        self._remember_command(text)
        self._set_state("thinking")
        self._log("YOU", text)
        threading.Thread(target=self._process_command, args=(text,), daemon=True).start()

    def _process_command(self, text: str) -> None:
        self.events.put(("state", "executing"))
        answer = self.router.handle(text)
        self.events.put(("answer", answer))

    def listen_voice(self) -> None:
        if self.is_listening:
            return
        if not self.voice.available:
            self._say("Voice recognition is not available, sir. Please check the microphone dependencies.")
            return
        self.is_listening = True
        self._set_state("listening")
        threading.Thread(target=self._listen_worker, daemon=True).start()

    def _listen_worker(self) -> None:
        text, error = self.voice.listen_once()
        self.events.put(("voice_done", text if text else error))

    def toggle_auto_voice(self) -> None:
        self.auto_voice = not self.auto_voice
        if self.auto_voice:
            self.listen_voice()

    def _drain_events(self) -> None:
        while True:
            try:
                kind, payload = self.events.get_nowait()
            except queue.Empty:
                break

            if kind == "answer":
                self._say(payload)
                if self.router.sleeping:
                    self.root.after(800, self.root.destroy)
                elif self.auto_voice:
                    self.root.after(1200, self.listen_voice)
            elif kind == "voice_done":
                self.is_listening = False
                if self._is_voice_error(payload):
                    self._set_state("error")
                    self._log("VOICE", payload)
                    if self.auto_voice:
                        self.root.after(250, self.listen_voice)
                elif payload:
                    self._submit_text(payload)
                elif self.auto_voice:
                    self._set_state("idle")
                    self.root.after(250, self.listen_voice)
            elif kind == "tts_error":
                self._set_state("error")
                self._log("VOICE", payload)
            elif kind == "state":
                self._set_state(payload)

        self.root.after(80, self._drain_events)

    @staticmethod
    def _is_voice_error(text: str) -> bool:
        return text.startswith(
            (
                "Khong nghe",
                "Toi khong nghe",
                "Voice loi",
                "SpeechRecognition",
                "Khong thu",
                "Speech recognition",
                "I could not understand",
                "Voice error",
                "No voice",
                "Could not record",
            )
        )

    def _say(self, text: str) -> None:
        self._set_state("speaking")
        self._log("JARVIS", text)
        threading.Thread(target=self._speak_worker, args=(text,), daemon=True).start()

    def _speak_worker(self, text: str) -> None:
        error = speak(text)
        if error:
            self.events.put(("tts_error", error))
        else:
            self.events.put(("state", "idle"))

    def _log(self, who: str, text: str) -> None:
        self.log.insert("end", f"{time.strftime('%H:%M:%S')}  {who}: {text}\n\n")
        self.log.see("end")

    def _set_state(self, state: str) -> None:
        self.ui_state = state
        suggestions = {
            "idle": "try: play Starboy song on spotify",
            "listening": "listening...",
            "thinking": "processing command...",
            "executing": "executing action...",
            "speaking": "speaking response...",
            "error": "check the log, sir",
        }
        self.suggestion_var.set(suggestions.get(state, suggestions["idle"]))

    def _remember_command(self, text: str) -> None:
        self.memory.add_command(text)
        self.history = self.memory.command_history()
        self.history_index = len(self.history)

    def _history_previous(self, _event: tk.Event) -> str:
        if not self.history:
            return "break"
        self.history_index = max(0, self.history_index - 1)
        self.input_var.set(self.history[self.history_index])
        return "break"

    def _history_next(self, _event: tk.Event) -> str:
        if not self.history:
            return "break"
        self.history_index = min(len(self.history), self.history_index + 1)
        self.input_var.set("" if self.history_index == len(self.history) else self.history[self.history_index])
        return "break"
