import os
import asyncio
import logging
from telethon import TelegramClient
from dotenv import load_dotenv

# Set up logging to console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load config
load_dotenv()
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

# Import the processing logic
from main import process_drama_full

async def main():
    # Use the session name from main.py
    client = TelegramClient('dramabox_bot', API_ID, API_HASH)
    await client.start(bot_token=BOT_TOKEN)
    
    # Test bookId found previously
    book_id = "42000005442" # Bangkitnya...
    
    print(f"🚀 Starting test upload for bookId: {book_id}")
    print(f"Target Check ID: {ADMIN_ID}")
    
    # Send initial status to user to confirm bot is awake
    status_msg = await client.send_message(ADMIN_ID, f"🚀 **Test Upload Manual Dimulai**\n🎬 Drama ID: `{book_id}`\n⏳ Memulai proses backend...")
    
    # Start the process
    # We will wrap the api call to limit episodes just for this test
    from api import get_all_episodes as get_all_episodes_real
    async def get_all_episodes_limited(bid):
        eps = await get_all_episodes_real(bid)
        return eps[:2] # JUST TEST 2 EPISODES
    
    import main
    main.get_all_episodes = get_all_episodes_limited
    
    success = await process_drama_full(book_id, ADMIN_ID, status_msg=status_msg)
    
    if success:
        print("✅ Test upload completed successfully.")
        await client.send_message(ADMIN_ID, "✅ **Test Upload Selesai.** Drama sudah masuk ke channel/chat ini.")
    else:
        print("❌ Test upload failed.")
        # If status_msg still exists (it might have been deleted on success)
        try:
            await status_msg.edit("❌ **Test Upload Gagal.** Mohon cek log terminal.")
        except:
             await client.send_message(ADMIN_ID, "❌ **Test Upload Gagal.** Mohon cek log terminal.")

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
