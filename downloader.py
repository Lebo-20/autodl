import os
import asyncio
import httpx
import logging

logger = logging.getLogger(__name__)

async def download_file(client: httpx.AsyncClient, url: str, path: str, ep_num: str):
    """Downloads a single file with potential progress tracking."""
    try:
        async with client.stream("GET", url) as response:
            if response.status_code != 200:
                logger.error(f"HTTP Error {response.status_code} for episode {ep_num}")
                return False
                
            with open(path, "wb") as f:
                async for chunk in response.aiter_bytes():
                    f.write(chunk)
        return True
    except Exception as e:
        logger.error(f"Failed to download {ep_num} from {url}: {e}")
        return False

async def download_all_episodes(episodes, download_dir: str, semaphore_count: int = 5):
    """
    Downloads all episodes concurrently.
    """
    os.makedirs(download_dir, exist_ok=True)
    semaphore = asyncio.Semaphore(semaphore_count)

    async def limited_download(ep):
        async with semaphore:
            ep_val = ep.get('chapterIndex') or ep.get('episode') or 'unk'
            ep_num = str(ep_val).zfill(3)
            filename = f"episode_{ep_num}.mp4"
            filepath = os.path.join(download_dir, filename)
            
            # Use videoUrl as primary for test if 1080p is tricky
            url = ep.get('videoUrl') or ep.get('1080p') or ep.get('720p') or ep.get('url')
            
            if not url:
                videos = ep.get('videos', [])
                if isinstance(videos, list) and videos:
                    url = videos[0].get('url')

            if not url:
                logger.error(f"No URL found for episode {ep_num}")
                return False
                
            async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
                success = await download_file(client, url, filepath, ep_num)
                if success:
                    logger.info(f"Successfully downloaded {filename}")
                return success

    results = await asyncio.gather(*(limited_download(ep) for ep in episodes))
    return all(results)
