from __future__ import annotations

from typing import TypedDict


class WorkflowStep(TypedDict):
    key: str
    instruction: str


__all__ = ["WorkflowStep"]

