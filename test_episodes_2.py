import asyncio
import json
from api import get_all_episodes

async def test_episodes():
    book_id = "42000005442" # Istriku, Aku Memang Dewa
    episodes = await get_all_episodes(book_id)
    if episodes:
        print(f"Total: {len(episodes)}")
        for i in range(max(len(episodes), 5)):
             print(f"Ep {i+1}: isCharge={episodes[i].get('isCharge')}, videoUrl={'Yes' if episodes[i].get('videoUrl') else 'No'}")

if __name__ == "__main__":
    asyncio.run(test_episodes())
