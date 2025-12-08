from __future__ import annotations

import logging
from functools import lru_cache

from core.config import get_settings
from core.constants import COLORS


def color_text(text: str, color: str | None = None) -> str:
    """Apply color to the given text if a color is provided."""
    return f"{color}{text}{COLORS['RESET']}" if color else text


class ColorFormatter(logging.Formatter):
    """Custom logging formatter to apply color to log messages."""

    def __init__(self, fmt: str, color: str | None = None):
        super().__init__(fmt)
        self.color = color

    def format(self, record: logging.LogRecord) -> str:
        base = super().format(record)
        return color_text(base, self.color)


@lru_cache(maxsize=8)
def get_logger(name: str = "chatbot.tools", color: str | None = None) -> logging.Logger:
    """Get a logger with a custom color formatter."""
    settings = get_settings()

    logger = logging.getLogger(name)
    logger.handlers.clear()
    logger.propagate = False

    handler = logging.StreamHandler()
    formatter = ColorFormatter("\n[%(name)s]\n%(message)s\n", color)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.setLevel(logging.DEBUG if settings.debug else logging.CRITICAL + 1)
    logger.disabled = not settings.debug

    return logger
