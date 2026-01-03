import asyncio
import websockets
import json

async def test_connection():
    uri = "ws://127.0.0.1:8000/admin/ws/dashboard"
    try:
        print(f"Connecting to {uri}...")
        async with websockets.connect(uri) as websocket:
            print("Connected!")
            
            # Wait for connection ack
            response = await websocket.recv()
            print(f"Received: {response}")
            
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
