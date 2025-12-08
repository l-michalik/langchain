from __future__ import annotations

import logging
from functools import lru_cache

from core.config import get_settings

BLUE = "\033[34m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RESET = "\033[0m"


def color_text(text: str, color: str | None = None) -> str:
    if not color:
        return text
    return f"{color}{text}{RESET}"


@lru_cache(maxsize=8)
def get_logger(name: str = "chatbot.tools", color: str | None = None) -> logging.Logger:
    settings = get_settings()

    logger = logging.getLogger(name)
    logger.handlers.clear()

    handler = logging.StreamHandler()

    class ColorFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            base = super().format(record)
            return color_text(base, color)

    formatter = ColorFormatter("\n--------------- [%(name)s] ---------------\n%(message)s\n------------------------------------------")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.propagate = False

    if settings.debug:
        logger.setLevel(logging.DEBUG)
        logger.disabled = False
    else:
        logger.setLevel(logging.CRITICAL + 1)
        logger.disabled = True

    return logger
