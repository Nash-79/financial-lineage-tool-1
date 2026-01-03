import asyncio
import websockets
import json

async def test_path(path):
    uri = f"ws://127.0.0.1:8000{path}"
    print(f"Testing URL: {uri}")
    try:
        async with websockets.connect(uri) as websocket:
            print(f"  [SUCCESS] Connected to {path}")
            await websocket.close()
    except Exception as e:
        print(f"  [FAILED] {e}")

async def main():
    paths = [
        "/admin/ws/dashboard",
        "/api/v1/ws/dashboard"
    ]
    for path in paths:
        await test_path(path)

if __name__ == "__main__":
    asyncio.run(main())
