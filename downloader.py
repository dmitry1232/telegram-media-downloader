# downloader.py
import argparse
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from telethon.sync import TelegramClient         # синхронный режим
from telethon import errors, types

HERE = Path(__file__).resolve().parent
load_dotenv(HERE / ".env")

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
PHONE = os.getenv("PHONE", "")
SESSION_NAME = os.getenv("SESSION_NAME", "session")

TME_C_RE = re.compile(r"https?://t\.me/c/(?P<chat_id>\d+)(?:/(?P<msg_id>\d+))?$")


def parse_chat_ref(ref: str):
    """@username | https://t.me/username | https://t.me/c/<id>/<msg> -> (entity_ref, start_msg_id)"""
    ref = ref.strip()
    m = TME_C_RE.fullmatch(ref)
    if m:
        raw = int(m.group("chat_id"))
        channel_id = int(f"-100{raw}")
        start_msg = int(m.group("msg_id")) if m.group("msg_id") else None
        return types.PeerChannel(channel_id), start_msg
    if ref.startswith("https://t.me/"):
        ref = ref.split("/")[-1]
    return ref, None


def ensure_dir(path: str) -> str:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return str(p.resolve())


def parse_date(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    raise ValueError(f"Bad date format: {s}. Use YYYY-MM-DD.")


def media_type_ok(msg, allowed: set) -> bool:
    if not msg or not msg.media:
        return False
    if not allowed:
        return True
    return (
        (msg.video and "video" in allowed)
        or (msg.photo and "photo" in allowed)
        or (msg.document and "document" in allowed)
        or (getattr(msg, "audio", None) and "audio" in allowed)
        or (getattr(msg, "voice", None) and "voice" in allowed)
        or (getattr(msg, "sticker", None) and "sticker" in allowed)
    )


def main():
    if not API_ID or not API_HASH:
        raise RuntimeError("API_ID or API_HASH is missing in .env")

    parser = argparse.ArgumentParser(description="Download Telegram media from a chat/channel.")
    parser.add_argument("--chat", required=True,
                        help="Chat: @username | https://t.me/username | https://t.me/c/<id>/<msg>")
    parser.add_argument("--save-dir", default=os.getenv("SAVE_DIR", str(HERE / "downloads")),
                        help="Folder to save files. Default: ./downloads")
    parser.add_argument("--types", default="", help="Comma-separated: video,photo,document,audio,voice,sticker.")
    parser.add_argument("--limit", type=int, default=0, help="Max messages to scan (0 = no limit).")
    parser.add_argument("--skip-existing", action="store_true", help="Skip files that already exist.")
    parser.add_argument("--min-id", type=int, default=None, help="Only messages with id >= MIN_ID.")
    parser.add_argument("--max-id", type=int, default=None, help="Only messages with id <= MAX_ID.")
    parser.add_argument("--since", type=str, default=None, help="Only from date (YYYY-MM-DD).")
    parser.add_argument("--until", type=str, default=None, help="Only up to date (YYYY-MM-DD).")
    parser.add_argument("--reverse", action="store_true", help="Iterate oldest→newest (default newest→oldest).")
    args = parser.parse_args()

    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    client.connect()

    # на всякий случай — если ещё не авторизован, спросим код/2FA
    if not client.is_user_authorized():
        print(f"Sending login code to {PHONE} ...")
        client.send_code_request(PHONE)
        code = input("Enter the code you received: ").strip()
        try:
            client.sign_in(phone=PHONE, code=code)
        except errors.SessionPasswordNeededError:
            pwd = input("Two-factor password: ")
            client.sign_in(password=pwd)

    entity_ref, start_msg = parse_chat_ref(args.chat)
    try:
        entity = client.get_entity(entity_ref)
    except Exception as e:
        client.disconnect()
        raise RuntimeError(f"Failed to resolve chat: {e}")

    save_dir = ensure_dir(args.save_dir)
    allowed = set(t.strip() for t in args.types.split(",") if t.strip()) if args.types else set()

    kwargs = {}
    if args.min_id:
        kwargs["min_id"] = args.min_id
    if args.max_id:
        kwargs["max_id"] = args.max_id
    if start_msg and not args.min_id:
        kwargs["min_id"] = start_msg
    date_from = parse_date(args.since)
    date_to = parse_date(args.until)

    title = getattr(entity, "title", None) or getattr(entity, "username", str(entity))
    print(f"Target: {title}")
    print(f"Save dir: {save_dir}")
    print(f"Filters: {','.join(sorted(allowed)) if allowed else 'none'}")
    print("Collecting messages...")

    count = 0
    try:
        for msg in client.iter_messages(entity, reverse=args.reverse, limit=args.limit or None, **kwargs):
            if date_from and msg.date.replace(tzinfo=None) < date_from:
                continue
            if date_to and msg.date.replace(tzinfo=None) > date_to:
                continue
            if not media_type_ok(msg, allowed):
                continue

            def progress(current: int, total: int):
                if total:
                    pct = int(current * 100 / total)
                    print(f"\rDownloading msg {msg.id} [{pct:3d}%]", end="", flush=True)

            try:
                path = msg.download_media(file=save_dir, progress_callback=progress)
                print(f"\rDownloaded: {Path(path).name}{' ' * 20}")
                count += 1
            except FileExistsError:
                if args.skip_existing:
                    print(f"Skip (exists): msg {msg.id}")
                    continue
                path = msg.download_media(file=save_dir, progress_callback=progress)
                print(f"\rDownloaded (dup): {Path(path).name}{' ' * 18}")
                count += 1
            except errors.FloodWaitError as fw:
                print(f"\nFlood wait: sleeping {fw.seconds}s...")
                import time; time.sleep(fw.seconds + 1)
            except Exception as e:
                print(f"\nFailed msg {msg.id}: {e}")
    finally:
        client.disconnect()

    print(f"\nDone. Downloaded files: {count}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    except Exception as e:
        print(f"Error: {e}")
