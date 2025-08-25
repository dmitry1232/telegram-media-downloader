from pathlib import Path
import os
from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon import errors

HERE = Path(__file__).resolve().parent
load_dotenv(HERE / ".env")  # <— грузим .env из корня проекта

api_id = int(os.getenv("API_ID", "0"))
api_hash = os.getenv("API_HASH", "")
phone = os.getenv("PHONE", "")

short_hash = (api_hash[:6] + "...") if api_hash else "(empty)"
print("[env]", api_id, short_hash, phone)

if not api_id or not api_hash:
    raise SystemExit("API_ID or API_HASH missing in .env")
if not phone.startswith("+"):
    print("WARNING: PHONE should be in international format, e.g. +380XXXXXXXXX")

client = TelegramClient("session", api_id, api_hash)

try:
    client.connect()
    if not client.is_user_authorized():
        print(f"[tg] sending login code to {phone} ...")
        client.send_code_request(phone)
        code = input("Enter the code you received: ").strip()
        try:
            client.sign_in(phone=phone, code=code)
        except errors.SessionPasswordNeededError:
            pwd = input("Two-factor password: ")
            client.sign_in(password=pwd)

    me = client.get_me()
    print("[tg] authorized as:", me.username or me.first_name)
    print("[tg] session file created at:", Path("session.session").resolve())
finally:
    client.disconnect()
