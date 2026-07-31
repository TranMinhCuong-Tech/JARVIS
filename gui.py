import math
import random
import tkinter as tk
from typing import Callable


class JarvisGUI:
    """
    Giao dien qua cau 3D voi cac hat tren be mat.
    Khi Agent phat am thanh, qua cau bien dang theo song.
    Khi khong noi, qua cau tu xoay cham.
    """

    def __init__(
        self, root: tk.Tk, on_submit_callback: Callable[[str], None] = None
    ):
        self.root = root
        self.root.title("AI Voice Agent - J.A.R.V.I.S")
        self.root.geometry("900x650")
        self.root.configure(bg="#000000")
        self.root.minsize(700, 500)

        self.on_submit_callback = on_submit_callback
        self.speaking = False
        self.time = 0.0
        self.status_var = tk.StringVar(value="Initializing...")

        # Cau hinh qua cau 3D
        self.particle_count = 450
        self.base_radius = 160
        self.fov = 300
        self.rotation_y = 0.0
        self.rotation_x = 0.3  # Nghieng mot chut de nhin ro 3D
        self.particles = self._generate_sphere_points(self.particle_count)

        # --- Trang thai cho cac hieu ung animation moi ---
        # Do "noi" duoc lam min dan (0.0 -> 1.0) thay vi bat/tat dot ngot,
        # giup qua cau bien dang mem mai hon khi chuyen trang thai.
        self.speaking_level = 0.0
        # Hieu ung "tho" nhe khi ranh (idle breathing)
        self.breath_phase = 0.0
        # Ngoi sao lam nen tao chieu sau cho khong gian
        self.stars = self._generate_starfield(90)
        # Goc quay cua 2 vong HUD ben ngoai (quay nguoc chieu nhau)
        self.ring_angle_a = 0.0
        self.ring_angle_b = 0.0
        # Hieu ung "flash" nhe khi co lenh moi duoc gui
        self.pulse_flash = 0.0

        self._build_ui()

    def _build_ui(self):
        # Canvas chinh cho qua cau 3D
        self.canvas = tk.Canvas(
            self.root, bg="#000000", highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        # Khung nhap lieu van ban o duoi cung
        input_frame = tk.Frame(self.root, bg="#000000")
        input_frame.pack(fill="x", side="bottom", padx=30, pady=(0, 15))

        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(
            input_frame,
            textvariable=self.entry_var,
            bg="#0a0a12",
            fg="#00d4ff",
            insertbackground="#00d4ff",
            font=("Consolas", 12),
            relief="flat",
            bd=8,
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 12))
        self.entry.bind("<Return>", lambda e: self._handle_send())

        send_btn = tk.Button(
            input_frame,
            text="SEND",
            command=self._handle_send,
            bg="#00111a",
            fg="#00d4ff",
            activebackground="#002233",
            activeforeground="#7efff5",
            font=("Consolas", 10, "bold"),
            relief="flat",
            bd=1,
            padx=28,
            pady=8,
        )
        send_btn.pack(side="right")

        # Label trang thai
        status_label = tk.Label(
            self.root,
            textvariable=self.status_var,
            bg="#000000",
            fg="#005577",
            font=("Consolas", 10),
            anchor="w",
        )
        status_label.pack(fill="x", side="bottom", padx=30, pady=(0, 5))

        # Bat dau vong lap animation
        self.animate()

    def _handle_send(self):
        text = self.entry_var.get().strip()
        self.entry_var.set("")
        if text and self.on_submit_callback:
            self.pulse_flash = 1.0  # kich hoat hieu ung nhap nhay khi gui lenh
            self.on_submit_callback(text)

    def set_status(self, text: str):
        self.status_var.set(text)

    def set_speaking(self, state: bool):
        """Duoc goi tu TTS de bat/tat hieu ung bien dang theo am thanh."""
        self.speaking = state

    def _generate_starfield(self, n: int):
        """Tao ngoi sao nen ngau nhien de tao chieu sau khong gian phia sau qua cau."""
        stars = []
        for _ in range(n):
            stars.append({
                "x": random.uniform(0.02, 0.98),   # ti le theo chieu rong canvas
                "y": random.uniform(0.02, 0.98),   # ti le theo chieu cao canvas
                "size": random.uniform(0.6, 1.8),
                "phase": random.uniform(0, math.pi * 2),
                "speed": random.uniform(0.6, 1.8),
            })
        return stars

    def _current_mode(self):
        """Xac dinh trang thai hien tai: speaking / processing / listening."""
        status_text = self.status_var.get().lower()
        if self.speaking:
            return "speaking"
        if "processing" in status_text:
            return "processing"
        return "listening"

    def _mode_palette(self, mode: str):
        """Tra ve mau sac chu dao (r, g, b he so 0-1) theo trang thai."""
        if mode == "speaking":
            return (0.25, 0.85, 1.0)
        if mode == "processing":
            return (1.0, 0.65, 0.15)
        return (0.05, 0.45, 0.85)

    def _generate_sphere_points(self, n: int):
        """Tao cac diem deu tren mat cau bang thuat toan Fibonacci sphere."""
        points = []
        golden_angle = math.pi * (3.0 - math.sqrt(5.0))
        for i in range(n):
            y = 1.0 - (i / (n - 1)) * 2.0  # y tu 1 den -1
            radius_at_y = math.sqrt(1.0 - y * y)
            theta = golden_angle * i
            x = math.cos(theta) * radius_at_y
            z = math.sin(theta) * radius_at_y
            points.append([x, y, z])
        return points

    def _rotate_point(self, x, y, z, ax, ay):
        """Xoay diem quanh truc X va Y."""
        # Xoay quanh truc Y
        cos_ay = math.cos(ay)
        sin_ay = math.sin(ay)
        x1 = x * cos_ay - z * sin_ay
        z1 = x * sin_ay + z * cos_ay
        # Xoay quanh truc X
        cos_ax = math.cos(ax)
        sin_ax = math.sin(ax)
        y1 = y * cos_ax - z1 * sin_ax
        z2 = y * sin_ax + z1 * cos_ax
        return x1, y1, z2

    def animate(self):
        self.time += 0.05
        self.breath_phase += 0.035

        # Do "noi" duoc lam min dan/tat dan (easing) thay vi nhay dot ngot,
        # giup chuyen dong tu nhien hon giua cac trang thai.
        target_level = 1.0 if self.speaking else 0.0
        self.speaking_level += (target_level - self.speaking_level) * 0.15

        # Hieu ung flash mo dan sau khi gui lenh
        self.pulse_flash = max(0.0, self.pulse_flash - 0.04)

        mode = self._current_mode()
        pr, pg, pb = self._mode_palette(mode)

        # Toc do xoay: nhanh dan theo muc do dang noi
        rot_speed = 0.008 + 0.009 * self.speaking_level
        self.rotation_y += rot_speed

        # Vong HUD ngoai xoay nguoc chieu nhau, nhanh hon khi dang xu ly/noi
        ring_speed = 0.006 + 0.02 * self.speaking_level
        if mode == "processing":
            ring_speed = 0.035
        self.ring_angle_a += ring_speed
        self.ring_angle_b -= ring_speed * 0.7

        self.canvas.delete("all")

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width < 10 or height < 10:
            width, height = 900, 550

        cx, cy = width / 2, height / 2 - 30

        # --- Nen: bau troi sao lap lanh, tao chieu sau khong gian ---
        for star in self.stars:
            twinkle = 0.5 + 0.5 * math.sin(self.time * star["speed"] + star["phase"])
            brightness = int(25 + 70 * twinkle)
            scolor = f"#{brightness:02x}{brightness:02x}{int(brightness*1.15):02x}"
            sx = star["x"] * width
            sy = star["y"] * height
            ssize = star["size"] * (0.7 + 0.6 * twinkle)
            self.canvas.create_oval(
                sx - ssize, sy - ssize, sx + ssize, sy + ssize,
                fill=scolor, outline=""
            )

        # Nhip "tho" nhe khi dang ranh (idle breathing) lam ban kinh dao dong cham
        breathing = math.sin(self.breath_phase) * (5.0 * (1.0 - self.speaking_level))

        # Tinh toan bien do song khi dang noi (lam min theo speaking_level)
        wave_intensity = (
            math.sin(self.time * 3.0) * 0.5 +
            math.sin(self.time * 7.2) * 0.3 +
            math.sin(self.time * 11.5) * 0.2
        ) * 18.0 * self.speaking_level

        # Xoay va chieu cac diem
        projected = []
        for i, (px, py, pz) in enumerate(self.particles):
            equator_factor = 1.0 - abs(py)  # 1 o xich dao, 0 o cuc
            phase = i * 0.1 + self.time * 2.0
            distortion = math.sin(phase) * wave_intensity * equator_factor

            r = self.base_radius + distortion + breathing
            x, y, z = self._rotate_point(px * r, py * r, pz * r,
                                         self.rotation_x, self.rotation_y)

            # Chieu perspective
            if z + self.fov <= 0:
                continue
            scale = self.fov / (self.fov + z)
            x2d = x * scale + cx
            y2d = y * scale + cy
            projected.append((x2d, y2d, z, scale, i))

        # Sap xep: ve diem xa truoc, gan sau (painter algorithm)
        projected.sort(key=lambda p: p[2])

        # Ve cac diem
        for x2d, y2d, z, scale, idx in projected:
            # Kich thuoc hat phu thuoc vao khoang cach Z
            base_size = 2.2 * scale
            size = max(1.0, base_size)

            # Mau sac phu thuoc vao mode hien tai (listening/processing/speaking)
            depth_factor = (z + self.base_radius) / (2 * self.base_radius)
            depth_factor = max(0.0, min(1.0, depth_factor))

            brightness = int(60 + 150 * (1.0 - depth_factor) + 60 * self.speaking_level)
            brightness = min(255, brightness)
            r = int(brightness * pr)
            g = int(brightness * pg)
            b = int(brightness * pb)
            glow = int(size * (1.5 + 1.2 * self.speaking_level))

            color = f"#{r:02x}{g:02x}{b:02x}"

            # Ve hat chinh
            self.canvas.create_oval(
                x2d - size, y2d - size,
                x2d + size, y2d + size,
                fill=color, outline=""
            )

            # Ve glow nhe xung quanh hat gan
            if scale > 0.6:
                glow_color = f"#{int(r*0.5):02x}{int(g*0.5):02x}{int(b*0.5):02x}"
                self.canvas.create_oval(
                    x2d - glow, y2d - glow,
                    x2d + glow, y2d + glow,
                    fill="", outline=glow_color, width=1
                )

        # Ve vong tron bao ngoai qua cau (outline tinh)
        outer_r = self.base_radius * (self.fov / (self.fov - self.base_radius * 0.5))
        self.canvas.create_oval(
            cx - outer_r, cy - outer_r,
            cx + outer_r, cy + outer_r,
            outline="#001a33", width=1
        )

        # Ve lop sang mo ben trong tao hieu ung "khi quyen"
        atmo_r = self.base_radius * 0.85
        self.canvas.create_oval(
            cx - atmo_r, cy - atmo_r,
            cx + atmo_r, cy + atmo_r,
            fill="", outline="#001122", width=2
        )

        # --- Vong HUD ngoai xoay, dang phan doan kieu radar/sci-fi ---
        hud_color = f"#{int(80*pr):02x}{int(80*pg):02x}{int(80*pb):02x}"
        hud_r1 = outer_r * 1.18
        hud_r2 = outer_r * 1.32
        segment_deg = 22
        gap_deg = 14
        for ring_r, base_angle, width_px in (
            (hud_r1, math.degrees(self.ring_angle_a), 2),
            (hud_r2, math.degrees(self.ring_angle_b), 1),
        ):
            angle = base_angle
            while angle < base_angle + 360:
                self.canvas.create_arc(
                    cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r,
                    start=angle, extent=segment_deg,
                    style="arc", outline=hud_color, width=width_px
                )
                angle += segment_deg + gap_deg

        # --- Hieu ung "flash" khi vua gui lenh: vong sang bung ra roi mo dan ---
        if self.pulse_flash > 0.0:
            flash_r = outer_r * (1.0 + 0.6 * (1.0 - self.pulse_flash))
            flash_bright = int(255 * self.pulse_flash)
            fcolor = f"#{int(flash_bright*pr):02x}{int(flash_bright*pg):02x}{int(flash_bright*pb):02x}"
            self.canvas.create_oval(
                cx - flash_r, cy - flash_r, cx + flash_r, cy + flash_r,
                outline=fcolor, width=2
            )

        # Hien thi trang thai tren qua cau, mau sac va noi dung theo mode
        if mode == "speaking":
            label_text = "SPEAKING"
            label_color = "#7efff5"
        elif mode == "processing":
            label_text = "PROCESSING"
            label_color = "#ffb347"
        else:
            label_text = "LISTENING"
            label_color = "#005577"

        # Nhe nhang nhap nhay (glow pulse) cho chu trang thai
        glow_pulse = 0.5 + 0.5 * math.sin(self.time * 2.2)
        label_y_offset = math.sin(self.time * 1.4) * 1.5  # boi len xuong nhe

        self.canvas.create_text(
            cx, cy + self.base_radius + 35 + label_y_offset,
            text=label_text,
            fill=label_color,
            font=("Consolas", 11, "bold")
        )
        self.canvas.create_text(
            cx, cy + self.base_radius + 55,
            text=self.status_var.get() if mode == "processing" else "Ask me anything",
            fill="#333344" if glow_pulse < 0.5 or mode != "processing" else "#553311",
            font=("Consolas", 9)
        )

        self.root.after(25, self.animate)
