"""
async_fetcher.py

An asynchronous HTTP fetcher with retry, timeout, and concurrency control.
Useful for concurrently requesting multiple URLs with robustness and CSV result export.

"""

import aiohttp
import asyncio
import csv
import time
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

class AsyncFetcher:
    """
    AsyncFetcher is a tool for concurrent URL fetching with retry, timeout,
    and result persistence.

    Attributes:
        urls (List[str]): A list of URLs to fetch.
        retries (int): Number of retry attempts for each URL.
        concurrency (int): Number of concurrent tasks allowed.
        timeout (int): Timeout (in seconds) per request.
        results (List[Dict]): List of successful fetch results.
    """

    def __init__(self, urls: List[str], retries: int = 3, concurrency: int = 5, timeout: int = 2):
        """
        Initialize the AsyncFetcher.

        Args:
            urls (List[str]): List of URLs to fetch.
            retries (int): Maximum retry attempts per URL.
            concurrency (int): Max number of concurrent tasks.
            timeout (int): Timeout per request in seconds.
        """
        self.urls = urls
        self.retries = retries
        self.concurrency = concurrency
        self.timeout = timeout
        self.semaphore = asyncio.Semaphore(concurrency)
        self.results: List[Dict] = []

    async def fetch_with_limit(self, session: aiohttp.ClientSession, url: str, idx: int):
        """Fetch a URL with concurrency control (semaphore)."""
        async with self.semaphore:
            await self._fetch(session, url, idx)

    async def _fetch(self, session: aiohttp.ClientSession, url: str, idx: int):
        """
        Core logic for fetching a URL with retries and timeout.

        Args:
            session (aiohttp.ClientSession): The aiohttp session.
            url (str): URL to fetch.
            idx (int): Task index for tracking.
        """
        for attempt in range(1, self.retries + 1):
            try:
                async with session.get(url, ssl=False, timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                    content = await response.text()
                    logging.info(f"Task {idx}: {url} fetched, length: {len(content)}")
                    self.results.append({
                        "id": idx,
                        "url": url,
                        "length": len(content),
                        "attempt": attempt
                    })
                    return
            except Exception as e:
                logging.warning(f"Task {idx}: Attempt {attempt} failed ({repr(e)})")
                await asyncio.sleep(0.5)
        logging.error(f"Task {idx}: Failed after {self.retries} attempts")

    async def run_async(self):
        """Run all fetch tasks (for async environments)."""
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.fetch_with_limit(session, url, idx)
                for idx, url in enumerate(self.urls)
            ]
            await asyncio.gather(*tasks)

    def run(self):
        """Run all fetch tasks in a blocking way (for CLI scripts)."""
        start = time.time()
        asyncio.run(self.run_async())
        end = time.time()
        logging.info(f"Total time: {end - start:.2f} seconds")

    def save_csv(self, filename: str = "results.csv"):
        """
        Save the results to a CSV file.

        Args:
            filename (str): Output file name (default: "results.csv").
        """
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "url", "length", "attempt"])
            writer.writeheader()
            writer.writerows(self.results)
        logging.info(f"Results saved to {filename}")
