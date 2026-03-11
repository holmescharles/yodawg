import logging

import requests

logger = logging.getLogger(__name__)

REDDIT_URL = "https://www.reddit.com/r/{subreddit}/.json"
HEADERS = {"User-Agent": "wallpaper-download"}
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")


def extract_gallery_urls(post, min_width=0):
    gallery_data = post.get("gallery_data")
    media_metadata = post.get("media_metadata")
    if not gallery_data or not media_metadata:
        return

    for item in gallery_data.get("items", []):
        media_id = item.get("media_id")
        meta = media_metadata.get(media_id)
        if not meta:
            continue

        width = meta.get("s", {}).get("x", 0)
        if width < min_width:
            continue

        mime = meta.get("m", "")
        ext = mime.split("/")[-1] if "/" in mime else ""
        if ext == "jpeg":
            ext = "jpg"
        if ext in ("jpg", "png"):
            yield f"https://i.redd.it/{media_id}.{ext}"


def extract_urls_from_page(page, min_width=0):
    for child in page.get("data", {}).get("children", []):
        post = child.get("data", {})
        url = post.get("url_overridden_by_dest", post.get("url", ""))

        if url.startswith("https://www.reddit.com/gallery/"):
            yield from extract_gallery_urls(post, min_width)
            continue

        if not url.lower().endswith(IMAGE_EXTENSIONS):
            continue

        preview = post.get("preview")
        if preview and min_width > 0:
            images = preview.get("images", [])
            if images:
                source = images[0].get("source", {})
                if source.get("width", 0) < min_width:
                    continue

        yield url


def fetch_pages(subreddit):
    after = None
    while True:
        params = {"limit": 100, "raw_json": 1}
        if after:
            params["after"] = after

        url = REDDIT_URL.format(subreddit=subreddit)
        logger.info("Fetching %s (after=%s)", url, after)

        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        page = response.json()

        yield page

        after = page.get("data", {}).get("after")
        if not after:
            break


def fetch_urls(subreddit="wallpaper", min_width=1920):
    for page in fetch_pages(subreddit):
        yield from extract_urls_from_page(page, min_width)
