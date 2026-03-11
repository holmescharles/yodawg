# AGENTS.md - Coding Agent Instructions for yodawg

## Project Overview

**yodawg** is a Python CLI application for downloading wallpapers from Reddit and
Wallhaven, then applying color schemes using pywal16. It's a personal "rice" utility.

**Tech Stack:** Python 3, asyncio, aiohttp, requests, Pillow, pywal16

**Entry Point:** `src/yodawg/cli.py:main()`

## Project Structure

```
src/yodawg/
├── cli.py           # Main CLI entry point (argparse)
├── rice.py          # Apply color scheme from wallpaper
├── download.py      # Async image downloading (aiohttp)
├── message.py       # Stderr logging utility
├── savewall.py      # Save current wallpaper
├── toosmall.py      # Filter small images
└── search/
    ├── urls.py      # Reddit URL fetching
    ├── reddit.py    # Reddit search main
    └── wallhaven.py # Wallhaven search main
```

## Build/Lint/Test Commands

### Installation

```bash
pip install -e .          # Editable/dev mode
pip install .             # Normal install
python -m build           # Build distribution
```

### Running

```bash
yodawg --help
yodawg search reddit wallpaper --count 100
yodawg search wallhaven "nature" --count 50
yodawg rice /path/to/image.jpg
yodawg rice -l            # light mode
yodawg save
```

### Linting

No linter is currently configured. If adding linting, use ruff:

```bash
ruff check src/                      # Lint all
ruff check src/yodawg/cli.py         # Lint single file
ruff check --fix src/                # Auto-fix
ruff format src/                     # Format
```

### Testing

**No tests exist yet.** If adding tests, use pytest:

```bash
pytest                                         # All tests
pytest tests/test_download.py                  # Single file
pytest tests/test_download.py::test_get_image  # Single function
pytest -v                                      # Verbose
```

## Code Style Guidelines

### Indentation

**Use 4 spaces.** (Note: Some files currently use 2 spaces - this is inconsistent
and should be normalized to 4 spaces when editing those files.)

Files with 2-space indent (legacy): `download.py`, `message.py`, `toosmall.py`,
`savewall.py`

Files with 4-space indent: `cli.py`, `rice.py`, `wallhaven.py`, `urls.py`, `reddit.py`

### Imports

Organize imports in this order with one blank line between groups:

1. Standard library imports
2. Third-party imports
3. Local imports (use relative imports with `.` and `..`)

```python
import asyncio
from pathlib import Path

import requests
from aiohttp import ClientSession

from ..message import message
from .urls import fetch_urls
```

### Naming Conventions

- **Functions:** `snake_case` (e.g., `fetch_reddit_page`, `download_images`)
- **Variables:** `snake_case` (e.g., `page_data`, `max_results`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `MAX_CONCURRENT`, `WALLPAPER_FOLDER`)
- **Files:** `snake_case` (e.g., `download.py`, `savewall.py`)

### Type Hints

Type hints are **not currently used** in this codebase. When adding new code,
type hints are optional but welcomed for function signatures.

### Strings

- Use **f-strings** for formatting
- Use **double quotes** for strings

### Error Handling

- Use `response.raise_for_status()` for HTTP errors
- Implement retry loops with backoff for network operations
- Log errors to stderr using `message()` from `message.py`
- Catch specific exceptions when possible, but `except Exception` is acceptable
  for top-level error handling

### Docstrings

Use **Google-style docstrings** (Args/Returns format) for functions that need documentation.

### Async Patterns

- Use `asyncio.run()` to run async code from sync entry points
- Use `asyncio.Semaphore` for concurrency limiting
- Use `asyncio.gather()` for parallel task execution

### CLI Patterns

- Use `argparse` for command-line parsing with subparsers for subcommands
- Lazy import modules in command handlers to improve startup time

### Logging

All user-facing messages go to **stderr** via `message()` from `message.py`.

### Path Handling

Use `pathlib.Path` for all file system operations.

## Key Constants

```python
WALLPAPER_FOLDER = Path.home() / "Downloads" / "Wallpapers"
MAX_CONCURRENT = 10
```

## Dependencies

requests, aiohttp, pillow, pywal16, colorz
