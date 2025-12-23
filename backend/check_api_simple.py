
import asyncio
import httpx

async def check_api():
    try:
        async with httpx.AsyncClient() as client:
            print("Checking Health...")
            resp = await client.get("http://127.0.0.1:8000/api/v1/health")
            print(f"Health: {resp.status_code} {resp.text}")

            print("Checking Register (Mock)...")
            # We won't actually register, just see if endpoint is reachable (422 for missing body)
            resp = await client.post("http://127.0.0.1:8000/api/v1/auth/register", json={})
            print(f"Register Resp: {resp.status_code}") # Should be 422, not 500

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_api())
