import asyncio
import json
from websockets.asyncio.client import connect
from app.utils.jwt import create_access_token
from app.schemas import Topic


async def test_ws():
    token = create_access_token({"sub": "script-test"})
    url = f"ws://localhost:8000/api/v1/ws?topic={Topic.ORDERS.value}&token={token}"

    print(f"🔌 Connecting to {url}")

    async with connect(url) as ws:
        print("✅ Connected!")

        try:
            while True:
                msg = await asyncio.wait_for(ws.recv(), timeout=10.0)
                print(f"📨 Received: {json.dumps(json.loads(msg), indent=2)}")
        except asyncio.TimeoutError:
            print("⏳ No messages received (normal if nothing published)")


if __name__ == "__main__":
    asyncio.run(test_ws())