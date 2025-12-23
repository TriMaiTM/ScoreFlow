
import asyncio
import httpx
from datetime import date

async def check_matches():
    try:
        async with httpx.AsyncClient() as client:
            # 1. Check Health (Correct URL)
            resp = await client.get("http://127.0.0.1:8000/health")
            print(f"✅ Health: {resp.status_code}")

            # 2. Check Matches By Date
            today = date.today().isoformat()
            print(f"Checking matches for {today}...")
            # Note: client is user (no auth needed? Let's check matches.py auth dependency)
            # matches.py seems to generally not require auth for GET, or maybe it does?
            # Looking at matches.py imports: router is APIRouter.
            # get_matches_by_date arguments: db, cache. No security dependency listed in the function signature!
            # So it should be public.
            
            resp = await client.get(f"http://127.0.0.1:8000/api/v1/matches/by-date?date={today}")
            
            if resp.status_code == 200:
                data = resp.json()
                print(f"✅ Matches API: 200 OK")
                print(f"   Success: {data.get('success')}")
                print(f"   Count: {data.get('data', {}).get('totalMatches')}")
            else:
                print(f"❌ Matches API Error: {resp.status_code}")
                print(f"   Body: {resp.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_matches())
