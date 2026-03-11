import argparse
import asyncio
import sys
from itertools import islice
from pathlib import Path

from .download import WALLPAPER_FOLDER, download_images


def log(*args):
    print(*args, file=sys.stderr)


def add_common_args(parser):
    parser.add_argument(
        "-n",
        "--count",
        type=int,
        default=200,
        help="max number of images to download (default: 200)",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="clear wallpaper folder before downloading",
    )
    parser.add_argument(
        "--min-width",
        type=int,
        default=1920,
        help="minimum image width in pixels (default: 1920)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=WALLPAPER_FOLDER,
        help=f"output directory (default: {WALLPAPER_FOLDER})",
    )


def handle_reddit(args):
    from .sources.reddit import fetch_urls

    urls = list(islice(fetch_urls(args.subreddit, args.min_width), args.count))
    log(f"Found {len(urls)} images from r/{args.subreddit}")

    if urls:
        asyncio.run(download_images(urls, args.output))


def handle_wallhaven(args):
    from .sources.wallhaven import fetch_urls

    urls = list(
        islice(
            fetch_urls(args.query, args.purity, args.categories, args.min_width),
            args.count,
        )
    )
    log(f"Found {len(urls)} images from wallhaven")

    if urls:
        asyncio.run(download_images(urls, args.output))


def main():
    parser = argparse.ArgumentParser(
        description="Download wallpapers from Reddit and Wallhaven",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="yodawg 0.3.0",
    )

    subparsers = parser.add_subparsers(dest="command")

    # reddit
    reddit = subparsers.add_parser("reddit", help="download from a subreddit")
    reddit.add_argument(
        "subreddit",
        nargs="?",
        default="wallpaper",
        help="subreddit name (default: wallpaper)",
    )
    add_common_args(reddit)

    # wallhaven
    wallhaven = subparsers.add_parser("wallhaven", help="search wallhaven")
    wallhaven.add_argument(
        "query",
        nargs="?",
        default="",
        help="search query",
    )
    wallhaven.add_argument(
        "--purity",
        default="100",
        help="purity filter: 1=sfw, 0=off per digit (sfw/sketchy/nsfw, default: 100)",
    )
    wallhaven.add_argument(
        "--categories",
        default="111",
        help="category filter: 1=on, 0=off per digit (general/anime/people, default: 111)",
    )
    add_common_args(wallhaven)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.clear:
        import shutil

        if args.output.exists():
            shutil.rmtree(args.output)
            log(f"Cleared {args.output}")

    before = len(list(args.output.glob("*"))) if args.output.exists() else 0

    if args.command == "reddit":
        handle_reddit(args)
    elif args.command == "wallhaven":
        handle_wallhaven(args)

    after = len(list(args.output.glob("*"))) if args.output.exists() else 0
    log(f"New images: {after - before}")
