import asyncio
import websockets
import json

async def test_connection(origin):
    uri = "ws://127.0.0.1:8000/admin/ws/dashboard"
    headers = {"Origin": origin} if origin else {}
    print(f"Testing Origin: '{origin}'")
    try:
        async with websockets.connect(uri, extra_headers=headers) as websocket:
            print(f"  [SUCCESS] Connected with origin: {origin}")
            await websocket.close()
    except Exception as e:
        print(f"  [FAILED] {e}")

async def main():
    # Test cases
    origins = [
        "http://localhost:8080",
        "http://localhost:8080/",
        "http://127.0.0.1:8080",
        None 
    ]
    
    for origin in origins:
        await test_connection(origin)

if __name__ == "__main__":
    asyncio.run(main())
