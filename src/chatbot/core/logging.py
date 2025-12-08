from __future__ import annotations

import logging
from functools import lru_cache

from core.config import get_settings


@lru_cache(maxsize=8)
def get_logger(name: str = "chatbot.tools") -> logging.Logger:
    """
    Return a logger configured to emit messages only when DEBUG setting is true.
    """
    settings = get_settings()

    logger = logging.getLogger(name)
    logger.handlers.clear()

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] [%(name)s] %(levelname)s - %(message)s"
    )
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

