import aiohttp
import asyncio

async def fetch(session, url):
    async with session.get(url, ssl=False) as response:
        content = await response.text()
        print(f"{url} fetched, length: {len(content)}")

async def main():
    urls = [
        "https://example.com",
        "https://httpbin.org/get",
        "https://jsonplaceholder.typicode.com/todos/1"
    ]

    async with aiohttp.ClientSession() as session:
        # TODO: 這裡用 gather 一起發送 fetch 任務
        await asyncio.gather(
            fetch(session, urls[0]),
            fetch(session, urls[1]),
            fetch(session, urls[2]),
        )

asyncio.run(main())
