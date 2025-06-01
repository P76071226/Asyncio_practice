import aiohttp
import asyncio
import time

MAX_RETRIES = 3
async def fetch(session, url, idx):
    for attempt in range(1, MAX_RETRIES+1):
        try:
            async with session.get(url, ssl=False, timeout=aiohttp.ClientTimeout(total=2)) as response:
                content = await response.text()
                print(f"Task {idx}: {url} fetched, length: {len(content)}")
                print(f"Success on attempt {attempt}")
                return
        except Exception as e:
            print(f"Task {idx}:Attempt {attempt} failed ({repr(e)})")
            await asyncio.sleep(2)
    print(f"Task {idx}: Failed after {MAX_RETRIES} attempts")

async def main():
    urls = [f"https://httpbin.org/delay/{i % 3}" for i in range(20)]

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
