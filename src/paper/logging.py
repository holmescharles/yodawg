import logging
import sys


def setup_logging() -> None:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    pkg = logging.getLogger("paper")
    pkg.setLevel(logging.INFO)
    pkg.addHandler(handler)
    pkg.propagate = False
