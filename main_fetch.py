from async_fetcher import AsyncFetcher

urls = [f"https://httpbin.org/delay/{i % 2}" for i in range(50)]

fetcher = AsyncFetcher(urls, retries=3, concurrency=5, timeout=2)
fetcher.run()
fetcher.save_csv("results.csv")
