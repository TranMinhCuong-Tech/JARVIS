"""
Auto-start module - dang ky J.A.R.V.I.S chay cung khi khoi dong may.
KHONG CAN API KEY. Ho tro Windows (Registry Run key), macOS (LaunchAgent),
va Linux (.desktop autostart entry).
"""
import os
import platform
import sys


def enable_auto_start(app_path: str = None) -> str:
    app_path = app_path or os.path.abspath(sys.argv[0])
    system = platform.system()

    try:
        if system == "Windows":
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE,
            )
            winreg.SetValueEx(key, "JARVIS", 0, winreg.REG_SZ, f'"{sys.executable}" "{app_path}"')
            winreg.CloseKey(key)
            return "Auto-start enabled, sir. I will launch automatically next time you log in."

        elif system == "Darwin":  # macOS
            plist_dir = os.path.expanduser("~/Library/LaunchAgents")
            os.makedirs(plist_dir, exist_ok=True)
            plist_path = os.path.join(plist_dir, "com.jarvis.autostart.plist")
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>com.jarvis.autostart</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{app_path}</string>
    </array>
    <key>RunAtLoad</key><true/>
</dict>
</plist>
"""
            with open(plist_path, "w") as f:
                f.write(plist_content)
            return "Auto-start enabled, sir. LaunchAgent installed."

        elif system == "Linux":
            autostart_dir = os.path.expanduser("~/.config/autostart")
            os.makedirs(autostart_dir, exist_ok=True)
            desktop_path = os.path.join(autostart_dir, "jarvis.desktop")
            desktop_content = f"""[Desktop Entry]
Type=Application
Name=JARVIS
Exec={sys.executable} {app_path}
X-GNOME-Autostart-enabled=true
"""
            with open(desktop_path, "w") as f:
                f.write(desktop_content)
            return "Auto-start enabled, sir. Desktop entry installed."

        return "Auto-start is not supported on this operating system, sir."
    except Exception as e:
        print(f"[Auto-start Error]: {e}")
        return "Sorry sir, I could not enable auto-start. Administrator rights may be required."


def disable_auto_start() -> str:
    system = platform.system()
    try:
        if system == "Windows":
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE,
            )
            winreg.DeleteValue(key, "JARVIS")
            winreg.CloseKey(key)
        elif system == "Darwin":
            path = os.path.expanduser("~/Library/LaunchAgents/com.jarvis.autostart.plist")
            if os.path.exists(path):
                os.remove(path)
        elif system == "Linux":
            path = os.path.expanduser("~/.config/autostart/jarvis.desktop")
            if os.path.exists(path):
                os.remove(path)
        return "Auto-start disabled, sir."
    except Exception as e:
        print(f"[Auto-start Disable Error]: {e}")
        return "Sorry sir, I could not disable auto-start."
