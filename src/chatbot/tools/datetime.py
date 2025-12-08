from __future__ import annotations

from datetime import timedelta

from langchain_core.tools import tool

from core.logging import get_logger
from schemas.tools import RelativeDateInput
from utils.datetime import apply_business_days, parse_datetime


@tool("relative_date", args_schema=RelativeDateInput)
def relative_date_tool(current_datetime: str, timezone: str, offset_days: int, day_type: str = "calendar") -> str:
    """Return a date offset from the given datetime in the specified timezone using calendar or business days."""
    logger = get_logger("chatbot.tools.relative_date")
    logger.debug(
        "Invoked with current_datetime=%s timezone=%s offset_days=%s day_type=%s",
        current_datetime,
        timezone,
        offset_days,
        day_type,
    )
    start = parse_datetime(current_datetime, timezone)
    if day_type == "business":
        target = apply_business_days(start, offset_days)
    else:
        target = start + timedelta(days=offset_days)
    return f"{target.date().isoformat()} ({target.strftime('%A')})"
