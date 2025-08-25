# 📥 Telegram Media Downloader

A simple Python script to download media (videos, photos, documents, etc.) from Telegram chats and channels using [Telethon](https://github.com/LonamiWebs/Telethon).

---

## ⚙️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/dmitry1232/telegram-media-downloader.git
cd telegram-media-downloader

### 2. Create a virtual environment
```bash
python -m venv .venv
.\.venv\Scripts\activate 

### 3. Install dependencies
```bash
pip install -r requirements.txt

### 4. Configure environment
Create a file named .env in the project root(.env.example):

API_ID=your_api_id
API_HASH=your_api_hash
PHONE=+380XXXXXXXXX
SESSION_NAME=session
SAVE_DIR=C:\Users\YourName\Desktop\Vids

### 5. Run authentication (first time only)
```bash
python auth_login.py

This will ask for a code from Telegram (and 2FA password if enabled).
After login, a session.session file will be created so you won’t need to enter codes again.

## Usage

#### Download 3 messages from a public channel
```bash
python downloader.py --chat "@channelname" --limit 3

#### Download all videos from a private channel
```bash
python downloader.py --chat "https://t.me/c/2164795256" --types video --save-dir "C:\Users\Vids"

#### Download starting from a specific message
```bash
python downloader.py --chat "https://t.me/c/2164795256/182" --reverse --limit 50

### Command-line options

--chat → Chat reference (@username, https://t.me/username, or https://t.me/c/<id>/<msg>). Required.

--save-dir → Folder to save files. Default: ./downloads or SAVE_DIR from .env.

--types → Comma-separated list of media types: video,photo,document,audio,voice,sticker. Empty = all.

--limit → Max number of messages to scan (0 = unlimited).

--skip-existing → Skip files that already exist.

--since / --until → Filter by date (YYYY-MM-DD).

--reverse → Iterate oldest → newest (default: newest → oldest).