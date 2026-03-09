import re
import os
import asyncio
import logging
import yt_dlp
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID"))

# Max concurrent downloads
CONCURRENT_DOWNLOADS = 25
download_semaphore = asyncio.Semaphore(CONCURRENT_DOWNLOADS)

# URL regex pattern
URL_PATTERN = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    await update.message.reply_text("Just paste any link (YouTube, TikTok, Instagram, etc.) and I'll download it automatically! 🚀")

async def process_single_video(url, update: Update):
    async with download_semaphore:
        status_message = await update.message.reply_text(f"Processing: {url}\nStatus: ⏳ Starting...")
        
        ydl_opts = {
            'format': 'mp4/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'concurrent_fragments': 32,
            'buffersize': 1024 * 1024 * 4,
            'retries': 15,
            'fragment_retries': 15,
            'external_downloader': 'aria2c',
            'external_downloader_args': [
                '--min-split-size=1M',
                '--max-connection-per-server=16',
                '--split=32',
                '--max-overall-download-limit=0',
                '--continue=true',
                '--allow-overwrite=true',
                '--file-allocation=none',
            ],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                await status_message.edit_text(f"Downloading: {url}\nStatus: 🚀 10MiB/s+")
                info = await asyncio.to_thread(ydl.extract_info, url, download=True)
                filename = ydl.prepare_filename(info)

            await status_message.edit_text(f"Uploading: {info.get('title', 'Video')}\nStatus: 📤 Sending...")
            
            try:
                with open(filename, 'rb') as video:
                    await update.message.reply_video(
                        video=video, 
                        caption=info.get('title', 'Video'),
                        read_timeout=300,
                        write_timeout=300,
                        connect_timeout=300,
                        pool_timeout=300
                    )
            except Exception as upload_err:
                logging.error(f"Upload error: {upload_err}")
                await status_message.edit_text(f"❌ Upload failed: {info.get('title', 'Video')}")
                return
            
            await status_message.delete()
            
            if os.path.exists(filename):
                os.remove(filename)

        except Exception as e:
            logging.error(f"Error processing {url}: {e}")
            await status_message.edit_text(f"❌ Error: {str(e)}")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logging.info(f"Received message from {user_id}: {update.message.text}")

    if user_id != ALLOWED_USER_ID:
        logging.warning(f"Unauthorized access attempt by ID: {user_id}")
        return

    # Extract ALL URLs from message
    message_text = update.message.text
    urls = re.findall(URL_PATTERN, message_text)
    
    if not urls:
        return
    
    # Process up to 25 URLs simultaneously
    tasks = []
    for url in urls[:CONCURRENT_DOWNLOADS]:
        tasks.append(process_single_video(url, update))
    
    if tasks:
        await asyncio.gather(*tasks)

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
        
    application = ApplicationBuilder().token(TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    # Detect links automatically in any text message
    video_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), download_video)
    
    application.add_handler(start_handler)
    application.add_handler(video_handler)
    
    print("Bot is running...")
    application.run_polling()
