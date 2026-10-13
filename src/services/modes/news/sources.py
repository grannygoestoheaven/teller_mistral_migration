# rr - FastAPI endpoint for news aggregation
import aiohttp
import asyncio

async def fetch_source(session: aiohttp.ClientSession, url: str) -> NewsItem:
    async with session.get(url) as response:
        data = await response.json()
        return NewsItem(
            title=data["headline"],
            source=url,
            summary=" ".join(data["summary"].split()[:30])
        )

async def fetch_news(topic: str) -> list[NewsItem]:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_source(session, url) for url in RELIABLE_SOURCES[topic]]
        return await asyncio.gather(*tasks)
