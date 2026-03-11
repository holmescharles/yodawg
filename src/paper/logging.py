import logging
import sys


def setup_logging() -> None:
    """Configure package-level logging with pywal-inspired colored output."""
    logging.addLevelName(logging.INFO, "\033[1;32mI\033[0m")
    logging.addLevelName(logging.WARNING, "\033[1;33mW\033[0m")
    logging.addLevelName(logging.ERROR, "\033[1;31mE\033[0m")
    logging.addLevelName(logging.DEBUG, "\033[1;34mD\033[0m")

    fmt = "[%(levelname)s] \033[1;31m%(module)s\033[0m: %(message)s"
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(fmt))

    pkg = logging.getLogger("paper")
    pkg.setLevel(logging.INFO)
    pkg.addHandler(handler)
    pkg.propagate = False
