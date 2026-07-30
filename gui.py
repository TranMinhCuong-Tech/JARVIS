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
            self.on_submit_callback(text)

    def set_status(self, text: str):
        self.status_var.set(text)

    def set_speaking(self, state: bool):
        """Duoc goi tu TTS de bat/tat hieu ung bien dang theo am thanh."""
        self.speaking = state

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

        # Toc do xoay: nhanh hon khi dang noi, cham khi binh thuong
        rot_speed = 0.008 if not self.speaking else 0.015
        self.rotation_y += rot_speed

        self.canvas.delete("all")

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width < 10 or height < 10:
            width, height = 900, 550

        cx, cy = width / 2, height / 2 - 30

        # Tinh toan bien do song khi dang noi
        wave_intensity = 0.0
        if self.speaking:
            # Tao nhieu tan so song chong len nhau de giong am thanh that
            wave_intensity = (
                math.sin(self.time * 3.0) * 0.5 +
                math.sin(self.time * 7.2) * 0.3 +
                math.sin(self.time * 11.5) * 0.2
            ) * 18.0  # Bien do pixel

        # Xoay va chieu cac diem
        projected = []
        for i, (px, py, pz) in enumerate(self.particles):
            # Bien dang theo song khi noi: cac diem gan "xich dao" dao dong manh hon
            distortion = 0.0
            if self.speaking:
                equator_factor = 1.0 - abs(py)  # 1 o xich dao, 0 o cuc
                phase = i * 0.1 + self.time * 2.0
                distortion = math.sin(phase) * wave_intensity * equator_factor

            r = self.base_radius + distortion
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

            # Mau sac: xanh duong cyan, sang hon khi gan va khi dang noi
            depth_factor = (z + self.base_radius) / (2 * self.base_radius)
            depth_factor = max(0.0, min(1.0, depth_factor))

            if self.speaking:
                # Khi noi: them mau trang/xanh sang vao cac hat
                brightness = int(100 + 155 * (1.0 - depth_factor))
                r = int(brightness * 0.3)
                g = int(brightness * 0.8)
                b = int(brightness)
                glow = int(size * 2.5)
            else:
                brightness = int(60 + 120 * (1.0 - depth_factor))
                r = int(brightness * 0.1)
                g = int(brightness * 0.5)
                b = int(brightness * 0.9)
                glow = int(size * 1.5)

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

        # Hien thi trang thai tren qua cau
        if self.speaking:
            label_text = "SPEAKING"
            label_color = "#7efff5"
        else:
            label_text = "LISTENING"
            label_color = "#005577"

        self.canvas.create_text(
            cx, cy + self.base_radius + 35,
            text=label_text,
            fill=label_color,
            font=("Consolas", 11, "bold")
        )
        self.canvas.create_text(
            cx, cy + self.base_radius + 55,
            text="Ask me anything",
            fill="#333344",
            font=("Consolas", 9)
        )

        self.root.after(25, self.animate)
