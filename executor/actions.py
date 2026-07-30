import os
import re
import subprocess
import time
import urllib.parse
import webbrowser
import pyautogui
import requests
import wikipedia
from datetime import datetime

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

_APP_NAME_TO_PROCESS = {
    "chrome": "chrome.exe",
    "google chrome": "chrome.exe",
    "edge": "msedge.exe",
    "firefox": "firefox.exe",
    "spotify": "Spotify.exe",
    "notepad": "notepad.exe",
    "cmd": "cmd.exe",
    "zalo": "Zalo.exe",
}


class ActionExecutor:
    """Component Action Executor - Thuc hien thao tac he thong, trinh duyet, Youtube & Spotify."""

    def play_on_youtube(self, media_name: str = None) -> str:
        """Mo YouTube tren trinh duyet va phat dung video goc cua bai hat/truy van."""
        if not media_name:
            webbrowser.open("https://www.youtube.com")
            return "Opening YouTube homepage, sir."

        print(f"[Executor]: Searching YouTube for '{media_name}'...")
        video_url = None

        if yt_dlp:
            try:
                ydl_opts = {
                    "format": "best",
                    "default_search": "ytsearch1",
                    "noplaylist": True,
                    "quiet": True,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(
                        f"ytsearch1:{media_name}", download=False
                    )
                    if "entries" in info and len(info["entries"]) > 0:
                        video_url = info["entries"][0]["webpage_url"]
            except Exception as e:
                print(f"[yt-dlp Warning]: {e}")

        if not video_url:
            query_encoded = urllib.parse.quote(media_name)
            video_url = (
                f"https://www.youtube.com/results?search_query={query_encoded}"
            )

        webbrowser.open(video_url)
        return f"Playing '{media_name}' on YouTube, sir."

    def play_on_spotify(self, media_name: str = None) -> str:
        """Mo Spotify qua URI tim kiem va click chuot truc tiep vao ket qua bai hat dau tien."""
        if not media_name:
            os.system('start spotify:')
            return "Opening Spotify application, sir."

        # 1. Lam sach tu khoa tim kiem bai hat
        cleaned_query = self._clean_spotify_query(media_name)
        print(f"[Executor]: Cleaned song name -> '{cleaned_query}'")

        # 2. Encode tu khoa sang dinh dang URI
        encoded_query = urllib.parse.quote(cleaned_query)

        # 3. Mo Spotify voi trang tim kiem da chuan bi san tu khoa
        spotify_uri = f"spotify:search:{encoded_query}"
        os.system(f'start "" "{spotify_uri}"')

        # 4. Doi Spotify duoc dua len toan man hinh/foreground va tai xong giao dien (3.5s)
        time.sleep(3.5)

        # 5. Lay kich thuoc man hinh hien tai de tinh toa do khu vuc Top Result cua Spotify
        screen_width, screen_height = pyautogui.size()

        # Vi tri the "Top Result" / "Ket qua hang dau" tren giao dien Spotify chuan:
        # Nam o khoang 35% chieu rong (ben trai) va 38% chieu cao man hinh tu tren xuong
        click_x = int(screen_width * 0.35)
        click_y = int(screen_height * 0.38)

        # 6. Di chuyen chuot toi vi tri bai hat va double-click de phat nhac
        print(f"[Executor]: Clicking mouse at coordinates ({click_x}, {click_y}) to play song...")
        pyautogui.moveTo(click_x, click_y, duration=0.3)
        pyautogui.doubleClick(click_x, click_y)

        return f"Opened Spotify, searched and clicked to play '{cleaned_query}', sir."

    def _clean_spotify_query(self, query: str) -> str:
        """Lam sach tu khoa tim kiem bai hat, bo cac tu du thua."""
        if not query:
            return ""

        noise_words = [
            r"\bsong\b",
            r"\btracks?\b",
            r"\bmusic\b",
            r"\bbai hat\b",
            r"\bbai\b",
            r"\bnhac\b",
            r"\bphat\b",
            r"\bchoi\b",
            r"\bplay\b",
            r"\bon spotify\b",
            r"\bspotify\b",
        ]

        cleaned = query.lower()
        for pattern in noise_words:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

        cleaned = " ".join(cleaned.split())
        return cleaned if cleaned else query

    def open_app(self, app_name: str) -> bool:
        if not app_name:
            return False
        pyautogui.press("win")
        time.sleep(0.5)
        pyautogui.write(app_name, interval=0.05)
        time.sleep(1.0)
        pyautogui.press("enter")
        return True

    def close_app(self, app_name: str) -> bool:
        if not app_name:
            return False
        key = app_name.strip().lower()
        process_name = _APP_NAME_TO_PROCESS.get(
            key, app_name.strip().replace(" ", "") + ".exe"
        )
        result = os.system(f'taskkill /F /IM "{process_name}" >nul 2>&1')
        return result == 0

    def control_system(self, action_text: str) -> str:
        """Dieu khien am luong va chup anh man hinh."""
        action_lower = action_text.lower()
        if "volume up" in action_lower or "increase volume" in action_lower:
            for _ in range(5):
                pyautogui.press("volumeup")
            return "Volume increased, sir."
        elif "volume down" in action_lower or "decrease volume" in action_lower:
            for _ in range(5):
                pyautogui.press("volumedown")
            return "Volume decreased, sir."
        elif "mute" in action_lower:
            pyautogui.press("volumemute")
            return "Mute toggled, sir."
        elif "screenshot" in action_lower:
            pictures_dir = os.path.join(os.path.expanduser("~"), "Pictures")
            filepath = os.path.join(
                pictures_dir, f"screenshot_{int(time.time())}.png"
            )
            pyautogui.screenshot(filepath)
            return "Screenshot saved to Pictures folder, sir."
        return "Command executed, sir."

    def search_web(self, query: str) -> str:
        if not query:
            return "No search query provided, sir."
        try:
            summary = wikipedia.summary(query, sentences=2)
            return f"According to Wikipedia, sir: {summary}"
        except Exception:
            webbrowser.open(
                f"https://www.google.com/search?q={urllib.parse.quote(query)}"
            )
            return f"Searching Google for '{query}', sir."

    def take_note(self, content: str) -> str:
        if not content:
            return "Note content is empty, sir."
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        notepath = os.path.join(desktop, "jarvis_notes.txt")
        with open(notepath, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {content}\n")
        return "I have written that down to jarvis_notes.txt on your Desktop, sir."

    # --- Cac tinh nang moi ---

    def get_time(self) -> str:
        """Tra ve thoi gian hien tai."""
        now = datetime.now()
        time_str = now.strftime("%I:%M %p")
        return f"The current time is {time_str}, sir."

    def get_date(self) -> str:
        """Tra ve ngay hien tai."""
        now = datetime.now()
        date_str = now.strftime("%A, %B %d, %Y")
        return f"Today is {date_str}, sir."

    def get_ip_address(self) -> str:
        """Lay dia chi IP public."""
        try:
            ip = requests.get("https://api.ipify.org", timeout=5).text
            return f"Your public IP address is {ip}, sir."
        except Exception:
            return "Sorry sir, I could not retrieve your IP address at the moment."

    def lock_computer(self) -> str:
        """Khoa man hinh may tinh."""
        os.system("rundll32.exe user32.dll,LockWorkStation")
        return "Locking your computer, sir."

    def shutdown_computer(self) -> str:
        """Tat may tinh."""
        os.system("shutdown /s /t 5")
        return "Shutting down your computer in 5 seconds, sir."

    def sleep_computer(self) -> str:
        """Dua may tinh vao che do ngu."""
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        return "Putting your computer to sleep, sir."
