import asyncio
import logging
import os
from pathlib import Path

import aiohttp

logger = logging.getLogger(__name__)

WALLPAPER_FOLDER = (
    Path(os.environ["WALLPAPER_FOLDER"])
    if "WALLPAPER_FOLDER" in os.environ
    else Path.home() / "Downloads" / "Wallpapers"
)
MAX_CONCURRENT = 10
MAX_RETRIES = 5
TIMEOUT = 30


async def fetch_image(session, url, semaphore):
    async with semaphore:
        for attempt in range(MAX_RETRIES):
            try:
                timeout = aiohttp.ClientTimeout(total=TIMEOUT)
                async with session.get(url, timeout=timeout) as response:
                    response.raise_for_status()
                    return await response.read()
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    delay = 1 + attempt
                    logger.warning(
                        "Retry %d/%d for %s: %s", attempt + 1, MAX_RETRIES, url, e
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error("Failed after %d attempts: %s", MAX_RETRIES, url)
                    return None


def filename_from_url(url):
    return url.split("/")[-1].split("?")[0]


async def download_images(urls, output=WALLPAPER_FOLDER):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)

    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    headers = {"User-Agent": "wallpaper-download"}

    async def download_one(url):
        name = filename_from_url(url)
        dest = output / name

        if dest.exists():
            logger.debug("Cached: %s", name)
            return

        data = await fetch_image(session, url, semaphore)
        if data:
            dest.write_bytes(data)
            logger.info("Downloaded: %s", name)

    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = [asyncio.create_task(download_one(url)) for url in urls]
        await asyncio.gather(*tasks)
