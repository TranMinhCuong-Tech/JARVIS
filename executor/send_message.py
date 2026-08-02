"""
Send Message module - gui tin nhan qua WhatsApp / Telegram, KHONG CAN API KEY.

WhatsApp: dung 'pywhatkit' de mo WhatsApp Web, tu dong go va nhan gui
(tuong tu co che 'Whatsapp automation' trong ban Jarvis truoc do cua ban).
Yeu cau: da dang nhap WhatsApp Web tren trinh duyet mac dinh it nhat 1 lan.

Telegram: khong co Bot API key nen khong the tu dong chon nguoi nhan va bam
gui thay ban duoc. Thay vao do, mo san Telegram Web/app voi noi dung tin
nhan da dien san trong khung soan tin - ban chi can chon nguoi nhan va bam
Gui. Day la gioi han that su khi khong dung Telegram Bot API.
"""
import json
import os
import time
import urllib.parse
import webbrowser

try:
    import pywhatkit
except ImportError:
    pywhatkit = None

_CONTACTS_PATH = os.path.join(os.path.dirname(__file__), "contacts.json")


def _load_contacts() -> dict:
    try:
        with open(_CONTACTS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {k.lower(): v for k, v in data.items() if not k.startswith("_")}
    except Exception:
        return {}


def _resolve_contact(name_or_number: str) -> str:
    """Neu la ten da luu trong contacts.json -> tra ve so dien thoai.
    Neu da la so dien thoai (bat dau bang + hoac toan chu so) -> giu nguyen."""
    cleaned = name_or_number.strip()
    if cleaned.startswith("+") or cleaned.replace(" ", "").isdigit():
        return cleaned.replace(" ", "")

    contacts = _load_contacts()
    return contacts.get(cleaned.lower())


def send_whatsapp(name_or_number: str, message: str) -> str:
    if not pywhatkit:
        return "WhatsApp sending requires the 'pywhatkit' package. Please install it."

    if not name_or_number:
        return "Who would you like to message on WhatsApp, sir?"
    if not message:
        return "What message would you like to send, sir?"

    phone = _resolve_contact(name_or_number)
    if not phone:
        return (
            f"I don't have '{name_or_number}' saved in contacts.json, sir. "
            f"Please add them there, or tell me the phone number directly."
        )

    try:
        # sendwhatmsg_instantly: mo WhatsApp Web ngay lap tuc, cho 'wait_time'
        # giay de trang tai xong roi tu dong nhan Enter de gui.
        pywhatkit.sendwhatmsg_instantly(
            phone_no=phone,
            message=message,
            wait_time=15,
            tab_close=True,
        )
        return f"Message sent to {name_or_number} on WhatsApp, sir."
    except Exception as e:
        print(f"[WhatsApp Error]: {e}")
        return (
            "Sorry sir, I could not send the WhatsApp message. "
            "Make sure you are logged into WhatsApp Web in your default browser."
        )


def send_telegram(message: str) -> str:
    """Mo Telegram Web voi noi dung tin nhan da dien san. Nguoi dung tu chon
    nguoi nhan va bam Gui, vi khong co Bot API key de tu dong hoa hoan toan."""
    if not message:
        return "What message would you like to send, sir?"

    encoded_msg = urllib.parse.quote(message)
    url = f"https://web.telegram.org/a/#?text={encoded_msg}"
    webbrowser.open(url)
    return (
        "I've opened Telegram Web with your message ready, sir. "
        "Please pick the recipient and press send, since I don't have a Telegram Bot key to do that step automatically."
    )
