import asyncio
import json
from api import get_latest_dramas, get_dubbed_dramas, get_foryou_dramas, get_popular_search

async def test_fetch():
    print("Fetching Latest...")
    latest = await get_latest_dramas()
    if latest:
        print(f"Latest (Top 3): {[d.get('title') or d.get('bookName') for d in latest[:3]]}")
        print(f"IDs: {[d.get('bookId') or d.get('id') for d in latest[:3]]}")
    
    print("\nFetching Dubbed...")
    dubbed = await get_dubbed_dramas()
    if dubbed:
         print(f"Dubbed (Top 3): {[d.get('title') or d.get('bookName') for d in dubbed[:3]]}")
         print(f"IDs: {[d.get('bookId') or d.get('id') for d in dubbed[:3]]}")

    print("\nFetching For You...")
    foryou = await get_foryou_dramas()
    if foryou:
         print(f"For You (Top 3): {[d.get('title') or d.get('bookName') for d in foryou[:3]]}")
         print(f"IDs: {[d.get('bookId') or d.get('id') for d in foryou[:3]]}")

    print("\nFetching Popular Search...")
    popular = await get_popular_search()
    if popular:
         if isinstance(popular, list):
             print(f"Popular (Top 3): {[d.get('title') or d.get('bookName') for d in popular[:3]]}")
             print(f"IDs: {[d.get('bookId') or d.get('id') for d in popular[:3]]}")
         else:
             print(f"Popular (Single): {popular.get('title') or popular.get('bookName')}")
             print(f"ID: {popular.get('bookId') or popular.get('id')}")

if __name__ == "__main__":
    asyncio.run(test_fetch())
