import aiohttp
import asyncio
import time

async def fetch(session, url, idx):
    async with session.get(url, ssl=False) as response:
        content = await response.text()
        print(f"Task {idx}: {url} fetched, length: {len(content)}")

async def main():
    urls = ["https://httpbin.org/delay/1" for _ in range(100)]

    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch(session, url, idx)
            for idx, url in enumerate(urls)
        ]
        await asyncio.gather(*tasks)

start = time.time()
asyncio.run(main())
end = time.time()

print(f"Total time: {end - start:.2f} seconds")
