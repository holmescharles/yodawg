import logging

import requests

logger = logging.getLogger(__name__)

WALLHAVEN_URL = "https://wallhaven.cc/api/v1/search"


def extract_urls_from_page(page):
    for item in page.get("data", []):
        path = item.get("path")
        if path:
            yield path


def fetch_pages(query, purity="100", categories="111", min_width=1920):
    page_num = 1
    while True:
        params = {
            "q": query,
            "purity": purity,
            "categories": categories,
            "page": page_num,
        }
        if min_width > 0:
            params["atleast"] = f"{min_width}x0"

        logger.info("Fetching wallhaven page %d (query=%r)", page_num, query)

        response = requests.get(WALLHAVEN_URL, params=params)
        response.raise_for_status()
        page = response.json()

        yield page

        last_page = page.get("meta", {}).get("last_page", 1)
        if page_num >= last_page:
            break
        page_num += 1


def fetch_urls(query="", purity="100", categories="111", min_width=1920):
    for page in fetch_pages(query, purity, categories, min_width):
        yield from extract_urls_from_page(page)
