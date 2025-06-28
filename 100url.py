"""
Asynchronous HTTP fetcher with concurrency control and retry logic.
Fetches 100 URLs concurrently (with a semaphore limit), retries on failure, and writes results to CSV.
"""
import aiohttp
import asyncio
import time
import csv
import logging
from typing import List, Dict

# Configurable parameters
MAX_RETRIES = 3
CONCURRENCY_LIMIT = 5
URL_COUNT = 100
TIMEOUT = 2

semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
results: List[Dict] = []

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def get_urls(n: int) -> List[str]:
    """Generate a list of URLs to fetch."""
    return [f"https://httpbin.org/delay/{i % 2}" for i in range(n)]

async def fetch_with_limit(session: aiohttp.ClientSession, url: str, idx: int) -> None:
    """Fetch a URL with concurrency limit."""
    logging.info(f"Task {idx} is running... ({semaphore._value} slots left)")
    async with semaphore:
        await fetch(session, url, idx)

async def fetch(session: aiohttp.ClientSession, url: str, idx: int) -> None:
    """Fetch a URL with retries and store the result."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with session.get(url, ssl=False, timeout=aiohttp.ClientTimeout(total=TIMEOUT)) as response:
                content = await response.text()
                logging.info(f"Task {idx}: {url} fetched, length: {len(content)}")
                results.append({
                    "id": idx,
                    "url": url,
                    "length": len(content),
                    "attempt": attempt
                })
                return
        except Exception as e:
            logging.warning(f"Task {idx}: Attempt {attempt} failed ({repr(e)})")
            await asyncio.sleep(0.5)
    logging.error(f"Task {idx}: Failed after {MAX_RETRIES} attempts")

async def main() -> None:
    """Main entry: create tasks, gather results, and write CSV."""
    urls = get_urls(URL_COUNT)
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_with_limit(session, url, idx) for idx, url in enumerate(urls)]
        await asyncio.gather(*tasks)
    with open("results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "url", "length", "attempt"])
        writer.writeheader()
        writer.writerows(results)

def run() -> None:
    start = time.time()
    asyncio.run(main())
    end = time.time()
    print(f"Total time: {end - start:.2f} seconds")

if __name__ == "__main__":
    run()
