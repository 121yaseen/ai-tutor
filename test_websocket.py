import asyncio
import websockets
import json

async def test_websocket():
    uri = 'ws://localhost:8000/run_live?app_name=agents&user_id=user&session_id=test123'
    try:
        async with websockets.connect(uri) as websocket:
            print('✅ WebSocket connection successful!')
            
            # Send a simple test message
            test_message = {
                'type': 'setup',
                'data': {
                    'model': 'gemini-2.0-flash-live-001'
                }
            }
            await websocket.send(json.dumps(test_message))
            print('✅ Test message sent')
            
            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f'✅ Received response: {response[:100]}...')
            
    except Exception as e:
        print(f'❌ WebSocket connection failed: {e}')

if __name__ == "__main__":
    asyncio.run(test_websocket()) 