"""
Game Updater - mo Steam / Epic Games Launcher de tu kich hoat qua trinh
kiem tra & tai cap nhat game. KHONG CAN API KEY (khong dung web API cua
Steam/Epic, chi khoi dong app va de chinh launcher tu xu ly update).
"""
import os
import platform
import subprocess

_STEAM_PATHS_WINDOWS = [
    r"C:\Program Files (x86)\Steam\steam.exe",
    r"C:\Program Files\Steam\steam.exe",
]
_EPIC_PATHS_WINDOWS = [
    r"C:\Program Files (x86)\Epic Games\Launcher\Portal\Binaries\Win32\EpicGamesLauncher.exe",
    r"C:\Program Files (x86)\Epic Games\Launcher\Portal\Binaries\Win64\EpicGamesLauncher.exe",
]


def _find_first_existing(paths):
    for path in paths:
        if os.path.exists(path):
            return path
    return None


def update_games(platform_name: str = "steam") -> str:
    system = platform.system()
    platform_name = platform_name.lower()

    if system != "Windows":
        # Tren macOS/Linux dua vao lenh 'open'/'xdg-open' voi ten app,
        # gia dinh nguoi dung da cai dat theo cach chuan cua OS.
        try:
            if system == "Darwin":
                subprocess.Popen(["open", "-a", "Steam" if platform_name == "steam" else "Epic Games Launcher"])
            else:
                subprocess.Popen(["xdg-open", "steam://open/main" if platform_name == "steam" else "epicgameslauncher"])
            return f"Launching {platform_name.title()} to check for game updates, sir."
        except Exception as e:
            print(f"[Game Updater Error]: {e}")
            return f"Sorry sir, I could not launch {platform_name.title()} on this system."

    if platform_name == "steam":
        exe = _find_first_existing(_STEAM_PATHS_WINDOWS)
        if exe:
            subprocess.Popen([exe, "-silent"])
            return "Launching Steam in the background to check for game updates, sir."
        return "Sorry sir, I could not find Steam installed on this system."

    elif platform_name == "epic":
        exe = _find_first_existing(_EPIC_PATHS_WINDOWS)
        if exe:
            subprocess.Popen([exe])
            return "Launching Epic Games Launcher to check for game updates, sir."
        return "Sorry sir, I could not find Epic Games Launcher installed on this system."

    return "Please specify 'steam' or 'epic', sir."
