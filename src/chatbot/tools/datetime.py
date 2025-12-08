from __future__ import annotations

from datetime import timedelta

from langchain_core.tools import tool
from core.logging import get_logger
from schemas.tools import RelativeDateInput
from utils.datetime import apply_business_days, parse_datetime
from core.constants import COLORS


@tool("relative_date", args_schema=RelativeDateInput)
def relative_date_tool(
    current_datetime: str, 
    timezone: str, 
    offset_days: int, 
    day_type: str = "calendar"
) -> str:
    """
    Calculate a date relative to another date. Invoke this tool only if user wants to get a relative date.

    Args:
        current_datetime (str): The starting date and time as a string.
        timezone (str): The timezone of the starting date and time.
        offset_days (int): The number of days to offset.
        day_type (str): The type of days to consider ("calendar" or "business").

    Returns:
        str: The calculated date in ISO format with the day of the week.
    """
    logger = get_logger("RELATIVE_DATE_TOOL", color=COLORS["GREEN"])
    start = parse_datetime(current_datetime, timezone)
    
    target = (
        apply_business_days(start, offset_days) 
        if day_type == "business" 
        else start + timedelta(days=offset_days)
    )
    
    result = f"{target.date().isoformat()} ({target.strftime('%A')})"
    logger.debug(result)
    return result
