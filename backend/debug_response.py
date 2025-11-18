import httpx
import asyncio
import json

async def check_latest():
    async with httpx.AsyncClient() as client:
        # Get settings to find a recent task
        try:
            # Try to start a quick test
            r = await client.post('http://localhost:8082/api/research/start', 
                                json={"topic": "test", "depth": "standard"})
            print("Start response:")
            print(json.dumps(r.json(), indent=2))
            
            task_id = r.json()['task_id']
            
            # Wait a bit
            await asyncio.sleep(10)
            
            # Check status
            r = await client.get(f'http://localhost:8082/api/research/{task_id}')
            print("\nStatus response structure:")
            data = r.json()
            print(json.dumps(data, indent=2))
            
        except Exception as e:
            print(f"Error: {e}")

asyncio.run(check_latest())
