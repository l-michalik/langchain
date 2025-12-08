from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class RelativeDateInput(BaseModel):
    current_datetime: str
    timezone: str
    offset_days: int
    day_type: Literal["calendar", "business"] = "calendar"


class SetActiveWorkflowInput(BaseModel):
    workflow: Literal["none", "brief", "project"]


__all__ = ["RelativeDateInput", "SetActiveWorkflowInput"]
