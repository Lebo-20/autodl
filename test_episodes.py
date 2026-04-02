import asyncio
import json
from api import get_all_episodes

async def test_episodes():
    book_id = "42000005442"
    print(f"Fetching episodes for {book_id}...")
    episodes = await get_all_episodes(book_id)
    if episodes:
        print(f"Total episodes: {len(episodes)}")
        print(f"First episode data: {json.dumps(episodes[0], indent=2)}")

if __name__ == "__main__":
    asyncio.run(test_episodes())
