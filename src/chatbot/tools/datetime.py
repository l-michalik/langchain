from __future__ import annotations

from datetime import timedelta

from langchain_core.tools import tool

from core.logging import get_logger
from schemas.tools import RelativeDateInput
from utils.datetime import apply_business_days, parse_datetime
from core.logging import GREEN

@tool("relative_date", args_schema=RelativeDateInput)
def relative_date_tool(current_datetime: str, timezone: str, offset_days: int, day_type: str = "calendar") -> str:
    """Use this tool as a helper to calculate a date offset from a given datetime in a specified timezone if user mention something about date"""
    logger = get_logger("RELATIVE_DATE_TOOL", color=GREEN)
    start = parse_datetime(current_datetime, timezone)
    if day_type == "business":
        target = apply_business_days(start, offset_days)
    else:
        target = start + timedelta(days=offset_days)
        
    res = f"{target.date().isoformat()} ({target.strftime('%A')})"
    logger.debug(res)
    return res
