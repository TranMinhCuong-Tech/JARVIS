from __future__ import annotations

import math
import queue
import random
import threading
import time
import tkinter as tk
from datetime import datetime
from tkinter import ttk

from .command_router import CommandRouter
from .speech import VoiceRecognizer, speak
from .system_info import day_period
from .user_memory import UserMemory

try:
    import psutil
except Exception:
    psutil = None


# ---------------------------------------------------------------------------
# Palette: state name -> (bright, dim, pale accent, pulse intensity)
# ---------------------------------------------------------------------------
STATE_PALETTE = {
    "boot": ("#7dffb0", "#1b8090", "#c4ffd9", 1.0),
    "idle": ("#55f6ff", "#1b8090", "#9ffcff", 1.0),
    "listening": ("#7dffb0", "#228f67", "#c4ffd9", 1.08),
    "thinking": ("#ffd45c", "#96772c", "#fff0b0", 1.14),
    "executing": ("#55f6ff", "#1b8090", "#ffffff", 1.18),
    "speaking": ("#ff6fd8", "#8c3278", "#ffd2f3", 1.1),
    "error": ("#ff566a", "#8d2632", "#ffd0d5", 1.05),
}

BG = "#050f16"
PANEL_BG = "#081821"
GRID_LINE = "#0b2531"
TEXT_DIM = "#4f97a4"


class JarvisUI:
    """Cinematic animated JARVIS HUD built with Tkinter."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("J.A.R.V.I.S.")
        self.root.geometry("1180x720")
        self.root.minsize(900, 560)
        self.root.configure(bg=BG)

        self.router = CommandRouter(on_reminder=self._on_reminder)
        self.memory = UserMemory()
        self.voice = VoiceRecognizer()
        self.events: queue.Queue[tuple[str, str]] = queue.Queue()

        self.is_listening = False
        self.auto_voice = True
        self.voice_out_enabled = True
        self.ui_state = "boot"
        self.history = self.memory.command_history()
        self.history_index = len(self.history)
        self.suggestion_var = tk.StringVar(value="starting up...")
        self.mic_label_var = tk.StringVar(value="MIC: ON")
        self.mute_label_var = tk.StringVar(value="VOICE: ON")

        self._phase = 0.0
        self._sweep_angle = 0.0
        self._boot_step = 0
        self._boot_lines = [
            "INITIALIZING JARVIS CORE...",
            "LOADING COMMAND MATRIX...",
            "CALIBRATING VOICE MODULE...",
            "LINKING SYSTEM SENSORS...",
            "ALL SYSTEMS NOMINAL.",
        ]
        self._dust = [
            (random.random() * math.tau, random.uniform(0.35, 1.12), random.uniform(0.4, 1.9))
            for _ in range(140)
        ]

        self._setup_style()
        self._build_layout()
        self._run_boot_sequence()

    def run(self) -> None:
        self.root.mainloop()

    # ------------------------------------------------------------------
    # Boot sequence
    # ------------------------------------------------------------------
    def _run_boot_sequence(self) -> None:
        self._animate()
        self._reveal_boot_line()

    def _reveal_boot_line(self) -> None:
        if self._boot_step < len(self._boot_lines):
            self.boot_text.set("\n".join(self._boot_lines[: self._boot_step + 1]))
            self._boot_step += 1
            self.root.after(320, self._reveal_boot_line)
        else:
            self.root.after(450, self._finish_boot)

    def _finish_boot(self) -> None:
        self.boot_overlay.place_forget()
        self._set_state("idle")
        self._say(self._startup_greeting())
        self._drain_events()
        self._tick_status_panels()
        self.root.after(900, self.listen_voice)

    def _startup_greeting(self) -> str:
        period = day_period()
        return f"Good {period}, sir. How can I help you today, sir?"

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def _setup_style(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Jarvis.TButton",
            background="#0a2530",
            foreground="#9fffff",
            borderwidth=1,
            padding=(12, 8),
            font=("Consolas", 10, "bold"),
        )
        style.map("Jarvis.TButton", background=[("active", "#104153")])
        style.configure(
            "Toggle.TButton",
            background="#0a2530",
            foreground="#c4ffd9",
            borderwidth=1,
            padding=(10, 6),
            font=("Consolas", 8, "bold"),
        )
        style.map("Toggle.TButton", background=[("active", "#123a2c")])

    def _build_layout(self) -> None:
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_columnconfigure(0, weight=1)

        self.hud = tk.Canvas(self.root, bg=BG, highlightthickness=0)
        self.hud.grid(row=0, column=0, sticky="nsew")

        command = tk.Frame(self.root, bg=BG)
        command.grid(row=1, column=0, sticky="ew", padx=34, pady=(0, 20))
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

        ttk.Button(command, text="SEND", style="Jarvis.TButton", command=self._submit_text).grid(row=0, column=1, padx=(0, 6))
        self.mic_button = ttk.Button(command, textvariable=self.mic_label_var, style="Toggle.TButton", command=self._toggle_mic)
        self.mic_button.grid(row=0, column=2, padx=(0, 6))
        self.mute_button = ttk.Button(command, textvariable=self.mute_label_var, style="Toggle.TButton", command=self._toggle_voice_out)
        self.mute_button.grid(row=0, column=3)

        tk.Label(
            command,
            textvariable=self.suggestion_var,
            bg=BG,
            fg="#5cb8c4",
            font=("Consolas", 9),
            anchor="w",
        ).grid(row=1, column=0, columnspan=4, sticky="ew", pady=(7, 0))

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
            state="normal",
        )
        self.log.tag_configure("you", foreground="#7dffb0", font=("Consolas", 9, "bold"))
        self.log.tag_configure("jarvis", foreground="#ffd45c", font=("Consolas", 9, "bold"))
        self.log.tag_configure("sys", foreground="#ff8f9d", font=("Consolas", 9, "bold"))
        self.log.tag_configure("time", foreground=TEXT_DIM, font=("Consolas", 8))
        self.log.tag_configure("body", foreground="#c3fbff")
        self.log_window = self.hud.create_window(0, 0, window=self.log, anchor="nw")

        # Boot overlay
        self.boot_overlay = tk.Frame(self.root, bg=BG)
        self.boot_text = tk.StringVar(value="")
        tk.Label(
            self.boot_overlay,
            text="J . A . R . V . I . S",
            fg="#7dffb0",
            bg=BG,
            font=("Consolas", 30, "bold"),
        ).pack(pady=(0, 18))
        tk.Label(
            self.boot_overlay,
            textvariable=self.boot_text,
            fg="#9ffcff",
            bg=BG,
            font=("Consolas", 11),
            justify="left",
        ).pack()
        self.boot_overlay.place(relx=0.5, rely=0.5, anchor="center")

    # ------------------------------------------------------------------
    # Animation loop
    # ------------------------------------------------------------------
    def _animate(self) -> None:
        self._phase += 0.024
        self._sweep_angle += 0.045
        self.hud.delete("hud")
        width = max(self.hud.winfo_width(), 900)
        height = max(self.hud.winfo_height(), 500)
        cx, cy = width / 2, height * 0.44
        r = min(width, height) * 0.24

        self._draw_background(width, height)
        self._draw_circular_hud(cx, cy, r)
        self._draw_corner_brackets(width, height)
        self._draw_status_panels(width, height)
        self._position_log(width, height)

        self.root.after(33, self._animate)

    def _draw_background(self, width: int, height: int) -> None:
        for x in range(0, width, 70):
            self.hud.create_line(x, 0, x, height, fill=GRID_LINE, tags="hud")
        for y in range(0, height, 70):
            self.hud.create_line(0, y, width, y, fill=GRID_LINE, tags="hud")
        # subtle vignette bars top/bottom
        self.hud.create_rectangle(0, 0, width, 3, fill="#0e3946", outline="", tags="hud")
        self.hud.create_rectangle(0, height - 3, width, height, fill="#0e3946", outline="", tags="hud")

    def _draw_corner_brackets(self, width: int, height: int) -> None:
        length = 34
        margin = 18
        color = "#2fb9c8"
        corners = [
            (margin, margin, 1, 1),
            (width - margin, margin, -1, 1),
            (margin, height - margin, 1, -1),
            (width - margin, height - margin, -1, -1),
        ]
        for x, y, dx, dy in corners:
            self.hud.create_line(x, y, x + length * dx, y, fill=color, width=2, tags="hud")
            self.hud.create_line(x, y, x, y + length * dy, fill=color, width=2, tags="hud")

    def _draw_status_panels(self, width: int, height: int) -> None:
        now = datetime.now()
        cyan, dim, pale, _ = STATE_PALETTE.get(self.ui_state, STATE_PALETTE["idle"])

        # Time / date panel (top-right)
        tx, ty = width - 210, 28
        self.hud.create_text(tx, ty, anchor="nw", text="TIME", fill=dim, font=("Consolas", 8, "bold"), tags="hud")
        self.hud.create_text(tx, ty + 14, anchor="nw", text=now.strftime("%H:%M:%S"), fill=cyan, font=("Consolas", 17, "bold"), tags="hud")
        self.hud.create_text(tx, ty + 40, anchor="nw", text=now.strftime("%A, %d %b %Y"), fill=pale, font=("Consolas", 9), tags="hud")

        # System panel (top-left)
        sx, sy = 28, 28
        self.hud.create_text(sx, sy, anchor="nw", text="SYSTEM", fill=dim, font=("Consolas", 8, "bold"), tags="hud")
        cpu, ram, battery = self._read_system_stats()
        self._status_bar(sx, sy + 18, 140, "CPU", cpu, cyan)
        self._status_bar(sx, sy + 36, 140, "MEM", ram, cyan)
        if battery is not None:
            self._status_bar(sx, sy + 54, 140, "BAT", battery, "#7dffb0" if battery > 25 else "#ff566a")

    def _status_bar(self, x: int, y: int, width: int, label: str, percent: float, color: str) -> None:
        self.hud.create_text(x, y, anchor="nw", text=label, fill=TEXT_DIM, font=("Consolas", 7), tags="hud")
        bar_x = x + 34
        bar_w = width - 34
        self.hud.create_rectangle(bar_x, y + 1, bar_x + bar_w, y + 8, outline="#153845", tags="hud")
        fill_w = max(1, int(bar_w * min(100.0, percent) / 100))
        self.hud.create_rectangle(bar_x, y + 1, bar_x + fill_w, y + 8, fill=color, outline="", tags="hud")

    def _read_system_stats(self) -> tuple[float, float, float | None]:
        if not psutil:
            return 0.0, 0.0, None
        try:
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory().percent
            battery = None
            if hasattr(psutil, "sensors_battery"):
                info = psutil.sensors_battery()
                if info is not None:
                    battery = float(info.percent)
            return float(cpu), float(ram), battery
        except Exception:
            return 0.0, 0.0, None

    def _tick_status_panels(self) -> None:
        # psutil.cpu_percent needs periodic sampling to stay accurate/non-blocking.
        if psutil:
            try:
                psutil.cpu_percent(interval=None)
            except Exception:
                pass
        self.root.after(1000, self._tick_status_panels)

    def _draw_circular_hud(self, cx: float, cy: float, r: float) -> None:
        cyan, dim, pale, pulse_scale = STATE_PALETTE.get(self.ui_state, STATE_PALETTE["idle"])
        state_pulse = 1.0 + 0.035 * pulse_scale * math.sin(self._phase * 5)

        # Soft outer glow simulated with stacked fading rings.
        for step in range(5, 0, -1):
            glow_r = r * (1.5 + step * 0.05) * state_pulse
            self.hud.create_oval(
                cx - glow_r, cy - glow_r, cx + glow_r, cy + glow_r,
                outline=self._fade(dim, step / 5), width=1, tags="hud",
            )

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

        # Radar sweep line, brighter while listening/thinking/executing.
        sweep_len = r * 1.45
        sweep_x = cx + math.cos(self._sweep_angle) * sweep_len
        sweep_y = cy + math.sin(self._sweep_angle) * sweep_len
        self.hud.create_line(cx, cy, sweep_x, sweep_y, fill=cyan, width=2, tags="hud")
        for trail in range(1, 6):
            trail_angle = self._sweep_angle - trail * 0.09
            tx = cx + math.cos(trail_angle) * sweep_len
            ty = cy + math.sin(trail_angle) * sweep_len
            self.hud.create_line(cx, cy, tx, ty, fill=self._fade(cyan, 1 - trail / 6), width=1, tags="hud")

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

        # Voice waveform bars while speaking.
        if self.ui_state == "speaking":
            self._draw_waveform(cx, cy + r * 1.75, r * 1.3, pale)

        core = r * 0.5
        self.hud.create_oval(cx - core, cy - core, cx + core, cy + core, fill="#092331", outline=cyan, width=3, tags="hud")
        self.hud.create_oval(cx - core * 0.78, cy - core * 0.78, cx + core * 0.78, cy + core * 0.78, outline="#113a48", width=2, tags="hud")
        self.hud.create_text(cx, cy - 2, text="J.A.R.V.I.S", fill="#bafcff", font=("Consolas", 14, "bold"), tags="hud")
        self.hud.create_text(cx, cy + 22, text=self.ui_state.upper(), fill=pale, font=("Consolas", 8), tags="hud")

    def _draw_waveform(self, cx: float, cy: float, width: float, color: str) -> None:
        bars = 24
        for index in range(bars):
            offset = (index - bars / 2) * (width / bars)
            amplitude = 6 + 14 * abs(math.sin(self._phase * 6 + index * 0.5))
            self.hud.create_line(
                cx + offset, cy - amplitude, cx + offset, cy + amplitude,
                fill=color, width=2, tags="hud",
            )

    @staticmethod
    def _fade(hex_color: str, factor: float) -> str:
        """Blend a hex color toward the background to fake transparency."""
        factor = max(0.0, min(1.0, factor))
        bg = (5, 15, 22)
        hex_color = hex_color.lstrip("#")
        r, g, b = (int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
        r = int(bg[0] + (r - bg[0]) * factor)
        g = int(bg[1] + (g - bg[1]) * factor)
        b = int(bg[2] + (b - bg[2]) * factor)
        return f"#{r:02x}{g:02x}{b:02x}"

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
        log_w = int(min(620, width * 0.66))
        log_h = 110
        x = int((width - log_w) / 2)
        y = int(height - log_h - 18)
        self.hud.coords(self.log_window, x, y)
        self.hud.itemconfigure(self.log_window, width=log_w, height=log_h)

    # ------------------------------------------------------------------
    # Command / voice handling
    # ------------------------------------------------------------------
    def _submit_text(self, value: str | None = None) -> None:
        text = value or self.input_var.get().strip()
        self.input_var.set("")
        if not text:
            return
        self._remember_command(text)
        self._set_state("thinking")
        self._log("YOU", text, "you")
        threading.Thread(target=self._process_command, args=(text,), daemon=True).start()

    def _process_command(self, text: str) -> None:
        self.events.put(("state", "executing"))
        answer = self.router.handle(text)
        self.events.put(("answer", answer))

    def listen_voice(self) -> None:
        if self.is_listening or not self.auto_voice:
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

    def _toggle_mic(self) -> None:
        self.auto_voice = not self.auto_voice
        self.mic_label_var.set(f"MIC: {'ON' if self.auto_voice else 'OFF'}")
        if self.auto_voice:
            self.listen_voice()

    def _toggle_voice_out(self) -> None:
        self.voice_out_enabled = not self.voice_out_enabled
        self.mute_label_var.set(f"VOICE: {'ON' if self.voice_out_enabled else 'OFF'}")

    def _on_reminder(self, message: str) -> None:
        self.events.put(("reminder", message))

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
                    self._log("VOICE", payload, "sys")
                    if self.auto_voice:
                        self.root.after(250, self.listen_voice)
                elif payload:
                    self._submit_text(payload)
                elif self.auto_voice:
                    self._set_state("idle")
                    self.root.after(250, self.listen_voice)
            elif kind == "tts_error":
                self._set_state("error")
                self._log("VOICE", payload, "sys")
            elif kind == "reminder":
                self._say(payload)
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
        self._log("JARVIS", text, "jarvis")
        threading.Thread(target=self._speak_worker, args=(text,), daemon=True).start()

    def _speak_worker(self, text: str) -> None:
        if not self.voice_out_enabled:
            self.events.put(("state", "idle"))
            return
        error = speak(text)
        if error:
            self.events.put(("tts_error", error))
        else:
            self.events.put(("state", "idle"))

    def _log(self, who: str, text: str, tag: str) -> None:
        self.log.insert("end", f"{time.strftime('%H:%M:%S')}  ", "time")
        self.log.insert("end", f"{who}: ", tag)
        self.log.insert("end", f"{text}\n\n", "body")
        self.log.see("end")

    def _set_state(self, state: str) -> None:
        self.ui_state = state
        suggestions = {
            "boot": "starting up...",
            "idle": "try: what's the weather, tell me a joke, take a screenshot",
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
