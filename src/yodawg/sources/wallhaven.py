import sys

import requests


WALLHAVEN_URL = "https://wallhaven.cc/api/v1/search"


def log(*args):
    print(*args, file=sys.stderr)


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

        log(f"Fetching wallhaven page {page_num} (query={query!r})")

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
