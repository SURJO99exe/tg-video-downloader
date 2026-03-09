# 🚀 Ultra-Fast Telegram Video Downloader

A high-speed, multi-threaded Telegram bot built with Python, `yt-dlp`, and `aria2c` to download videos from 1000+ sites (YouTube, TikTok, Instagram, Twitter, etc.) at maximum speed.

## ✨ Features
- **Ultra-Fast Downloads**: Uses `aria2c` with 32 connections for IDM-like speeds (10MiB/s+).
- **Multi-URL Support**: Paste up to 25 links in a single message to download them all simultaneously.
- **Automatic Detection**: Just send a link, and the bot handles the rest.
- **MP4 Optimization**: Automatically converts/downloads the best MP4 format for Telegram compatibility.
- **Secure**: Only authorized users (defined in `.env`) can use the bot.

## 🛠️ Prerequisites
- Python 3.8+
- [aria2c](https://aria2.github.io/) installed and added to your system PATH.

## 🚀 Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/SURJO99exe/tg-video-downloader.git
   cd tg-video-downloader
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and fill in your details:
   - `TELEGRAM_BOT_TOKEN`: Get this from [@BotFather](https://t.me/BotFather).
   - `ALLOWED_USER_ID`: Get your ID from [@userinfobot](https://t.me/userinfobot).

5. **Run the Bot**:
   ```bash
   python bot.py
   ```

## 📝 Usage
Send one or multiple video links to the bot. It will automatically detect them, start the high-speed download, and send the video files back to you.

## 📄 License
MIT
