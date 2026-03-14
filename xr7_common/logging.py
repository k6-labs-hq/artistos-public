from __future__ import annotations

import logging
import os


_LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"


def configure_logging() -> None:
    level = os.getenv("XR7_LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=level, format=_LOG_FORMAT)


def get_logger(name: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)
