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
    current = datetime.now(tz)
    return current.isoformat(), tz.key


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
    remaining = abs(offset)
    current = start
    while remaining > 0:
        current += timedelta(days=step)
        if current.weekday() < 5:
            remaining -= 1
    return current
