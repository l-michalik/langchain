from __future__ import annotations

from typing import TypedDict


class WorkflowStep(TypedDict):
    key: str | None
    instruction: str


__all__ = ["WorkflowStep"]

