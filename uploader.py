import os
import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import DocumentAttributeVideo
import logging

logger = logging.getLogger(__name__)

async def upload_progress(current, total, event, msg_text="Uploading..."):
    """Callback function for upload progress."""
    percentage = (current / total) * 100
    try:
        # Avoid flood by updating every few percentages
        if int(percentage) % 10 == 0:
            await event.edit(f"{msg_text} {percentage:.1f}%")
    except:
        pass

async def upload_drama(client: TelegramClient, chat_id: int, 
                       title: str, description: str, 
                       poster_url: str, video_path: str):
    """
    Uploads the drama information and merged video to Telegram.
    """
    import subprocess
    import tempfile
    try:
        # 1. Send Poster + Description
        caption = f"🎬 **{title}**\n\n📝 **Sinopsis:**\n{description[:500]}..." # Limit caption length
        
        # Send Photo with Caption
        sent_info = await client.send_file(
            chat_id,
            poster_url,
            caption=caption,
            parse_mode='html'
        )
        
        status_msg = await client.send_message(chat_id, "📤 Ekstraksi Thumbnail & Durasi Video...")
        
        # 2. Extract Duration & Dimensions (Fallback directly if fails)
        duration = 0
        width = 0
        height = 0
        try:
            ffprobe_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=width,height", "-of", "default=noprint_wrappers=1:nokey=1", video_path]
            output = subprocess.check_output(ffprobe_cmd, text=True).strip().split('\n')
            if len(output) >= 3:
                width = int(output[0])
                height = int(output[1])
                duration = int(float(output[2]))
        except Exception as e:
            logger.warning(f"Failed to extract video info: {e}")

        # 3. Extract Thumbnail
        thumb_path = os.path.join(tempfile.gettempdir(), f"thumb_{os.path.basename(video_path)}.jpg")
        try:
            subprocess.run(["ffmpeg", "-y", "-i", video_path, "-ss", "00:00:01.000", "-vframes", "1", thumb_path], capture_output=True)
            if not os.path.exists(thumb_path):
                thumb_path = None
        except Exception as e:
            logger.warning(f"Failed to generate thumbnail: {e}")
            thumb_path = None

        await status_msg.edit("📤 Sedang mengupload video ke Telegram...")
        
        from telethon.tl.types import DocumentAttributeVideo
        video_attributes = [
            DocumentAttributeVideo(
                duration=duration,
                w=width,
                h=height,
                supports_streaming=True
            )
        ]
        
        await client.send_file(
            chat_id,
            video_path,
            caption=f"🎥 Full Episode: {title}",
            force_document=False, # FORCE IT AS VIDEO STREAM
            thumb=thumb_path,
            attributes=video_attributes,
            progress_callback=lambda c, t: upload_progress(c, t, status_msg, "Upload Video:"),
            supports_streaming=True
        )
        
        await status_msg.delete()
        if thumb_path and os.path.exists(thumb_path):
            os.remove(thumb_path)
            
        logger.info(f"Successfully uploaded {title} to Telegram")
        return True
    except Exception as e:
        logger.error(f"Failed to upload to Telegram: {e}")
        return False
