import httpx
import asyncio
import json

async def check_task():
    async with httpx.AsyncClient() as client:
        r = await client.get('http://localhost:8081/api/research/f05df1a7-e0cd-4c5f-9950-53d4765c6167')
        data = r.json()
        print(json.dumps(data, indent=2))

asyncio.run(check_task())
