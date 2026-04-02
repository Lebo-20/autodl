import os
import asyncio
import logging
import tempfile
import shutil
from telethon import TelegramClient
from dotenv import load_dotenv

def log_test(msg):
    with open("test_status.txt", "a", encoding="utf-8") as f:
        f.write(msg + "\n")

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load config
load_dotenv()
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

# Imports
from api import get_drama_detail, get_all_episodes
from downloader import download_all_episodes
from merge import merge_episodes
from uploader import upload_drama

async def run_standalone_test(book_id: str):
    if os.path.exists("test_status.txt"): os.remove("test_status.txt")
    
    client = TelegramClient('test_session', API_ID, API_HASH)
    await client.start(bot_token=BOT_TOKEN)
    
    chat_id = ADMIN_ID
    log_test(f"🚀 Standalone test for {book_id}")
    
    try:
        detail = await get_drama_detail(book_id)
        if not detail:
            log_test("❌ Detail not found.")
            return

        all_eps = await get_all_episodes(book_id)
        if not all_eps:
             log_test("❌ Episodes not found.")
             return
             
        episodes = all_eps[:2]
        
        title = detail.get("title") or detail.get("bookName") or f"Drama_{book_id}"
        description = detail.get("intro") or detail.get("introduction") or "Description"
        poster = detail.get("cover") or detail.get("coverWap") or ""

        temp_dir = tempfile.mkdtemp(prefix=f"test_dramabox_")
        video_dir = os.path.join(temp_dir, "episodes")
        os.makedirs(video_dir, exist_ok=True)
        
        try:
            log_test(f"⏳ Downloading 2 episodes of {title}...")
            dl_success = await download_all_episodes(episodes, video_dir)
            if not dl_success:
                 log_test("❌ Download partially failed.")
            
            log_test("⏳ Merging episodes...")
            output_video_path = os.path.join(temp_dir, f"test_{book_id}.mp4")
            merge_success = merge_episodes(video_dir, output_video_path)
            if not merge_success:
                 log_test("❌ Merge failed.")
                 return
            
            log_test(f"⏳ Uploading to chat {chat_id}...")
            upload_success = await upload_drama(
                 client, chat_id, 
                 title + " (TEST_SUCCESS)", description, 
                 poster, output_video_path
            )
            
            if upload_success:
                 log_test("✅ STANDALONE TEST FINISHED SUCCESS.")
            else:
                 log_test("❌ STANDALONE TEST FAILED AT UPLOAD.")
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    except Exception as e:
        log_test(f"🚨 Standalone test error: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    import sys
    bid = sys.argv[1] if len(sys.argv) > 1 else "42000005442"
    asyncio.run(run_standalone_test(bid))
