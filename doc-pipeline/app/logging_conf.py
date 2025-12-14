import logging
from logging import Formatter, StreamHandler


def setup_logging(level: int = logging.INFO) -> None:
    root = logging.getLogger()
    if root.handlers:
        return
    root.setLevel(level)
    h = StreamHandler()
    h.setFormatter(Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))
    root.addHandler(h)
