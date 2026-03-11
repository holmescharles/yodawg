import logging

import requests

logger = logging.getLogger(__name__)

NASA_URL = "https://images-api.nasa.gov/search"

PEOPLE_KEYWORDS = {
    "scientists",
    "panelist",
    "panelists",
    "audience",
    "moderator",
    "administrator",
    "meeting",
    "conference",
    "ceremony",
    "portrait",
}


def has_people(item):
    """Heuristic check for people/event photos."""
    data = item.get("data", [{}])[0]

    if data.get("photographer"):
        return True
    if data.get("location"):
        return True

    keywords = {k.lower() for k in data.get("keywords", [])}
    if keywords & PEOPLE_KEYWORDS:
        return True

    return False


def extract_urls_from_page(page, include_people=False):
    for item in page.get("collection", {}).get("items", []):
        if not include_people and has_people(item):
            continue

        for link in item.get("links", []):
            if link.get("rel") == "preview":
                # preview is a thumbnail; get the full-res asset
                href = link.get("href", "")
                if href:
                    yield href
                break


def get_asset_url(nasa_id):
    """Fetch the original full-res image URL for a given nasa_id."""
    response = requests.get(f"https://images-api.nasa.gov/asset/{nasa_id}")
    response.raise_for_status()
    items = response.json().get("collection", {}).get("items", [])

    for item in items:
        href = item.get("href", "")
        if "~orig" in href and href.lower().endswith((".jpg", ".jpeg", ".png", ".tif")):
            return href

    # fall back to largest available
    for item in reversed(items):
        href = item.get("href", "")
        if href.lower().endswith((".jpg", ".jpeg", ".png")):
            return href

    return None


def fetch_pages(query, center=None):
    page_num = 1
    while True:
        params = {
            "q": query,
            "media_type": "image",
            "page": page_num,
        }
        if center:
            params["center"] = center

        logger.info("Fetching NASA page %d (query=%r)", page_num, query)

        response = requests.get(NASA_URL, params=params)
        response.raise_for_status()
        page = response.json()

        collection = page.get("collection", {})
        items = collection.get("items", [])
        if not items:
            break

        yield page

        # check for next page
        links = collection.get("links", [])
        has_next = any(link.get("rel") == "next" for link in links)
        if not has_next:
            break
        page_num += 1


def fetch_urls(query="space", center=None, include_people=False):
    for page in fetch_pages(query, center):
        items = page.get("collection", {}).get("items", [])
        for item in items:
            if not include_people and has_people(item):
                continue

            data = item.get("data", [{}])[0]
            nasa_id = data.get("nasa_id")
            if not nasa_id:
                continue

            url = get_asset_url(nasa_id)
            if url:
                yield url
