import asyncio
import httpx
from api import BASE_URL, DEFAULT_LANG, AUTH_CODE

async def debug_homepage():
    async with httpx.AsyncClient() as client:
        url = f"{BASE_URL}/homepage"
        params = {"lang": DEFAULT_LANG, "code": AUTH_CODE}
        print(f"Checking homepage with code: {AUTH_CODE}")
        try:
            resp = await client.get(url, params=params)
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.text[:500]}")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(debug_homepage())
