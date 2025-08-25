# Telegram Media Downloader

A simple Python script to download media (videos, photos, documents, etc.) from Telegram chats and channels using [Telethon](https://github.com/LonamiWebs/Telethon).

## Installation


# Clone the repository
git clone https://github.com/dmitry1232/telegram-media-downloader.git
cd telegram-media-downloader

# Create a virtual environment
python -m venv .venv
.\.venv\Scripts\activate   # Windows PowerShell

# Install dependencies
pip install -r requirements.txt

# Run the authentication script once:
python auth_login.py
# A session.session file will be created — this stores your login so you won’t need to enter codes every time.

## Usage

# Download 3 messages from a public channel
python downloader.py --chat "@channelname" --limit 3

# Download all videos from a private channel
python downloader.py --chat "https://t.me/c/2164795256" --types video --save-dir "C:\Users\Vids"

# Download starting from a specific message
python downloader.py --chat "https://t.me/c/2164795256/182" --reverse --limit 50

Command-line options

--chat — Chat reference (@username, https://t.me/username, or https://t.me/c/<id>/<msg>). Required.

--save-dir — Folder to save files. Default: ./downloads or SAVE_DIR from .env.

--types — Comma-separated list of media types: video,photo,document,audio,voice,sticker. Empty = all.

--limit — Maximum number of messages to scan (0 = unlimited).

--skip-existing — Skip files that already exist.

--since / --until — Filter by date (YYYY-MM-DD).

--reverse — Iterate oldest → newest (default: newest → oldest).