from __future__ import annotations
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

def resolve_timezone(tz_name: str) -> ZoneInfo:
    try:
        return ZoneInfo(tz_name)
    except (ZoneInfoNotFoundError, ValueError):
        return ZoneInfo("UTC")

def now_iso_in_timezone(tz_name: str) -> tuple[str, str]:
    tz = resolve_timezone(tz_name)
    return datetime.now(tz).isoformat(), tz.key

def parse_datetime(value: str, tz_name: str) -> datetime:
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        dt = datetime.now(ZoneInfo("UTC"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=resolve_timezone(tz_name))
    return dt.astimezone(resolve_timezone(tz_name))

def apply_business_days(start: datetime, offset: int) -> datetime:
    step = 1 if offset >= 0 else -1
    current = start
    for _ in range(abs(offset)):
        current += timedelta(days=step)
        while current.weekday() >= 5:
            current += timedelta(days=step)
    return current
