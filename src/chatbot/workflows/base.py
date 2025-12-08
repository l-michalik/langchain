from __future__ import annotations
from typing import Any, Callable, TypedDict

ValidatorFn = Callable[[Any], tuple[bool, str | None]]
class WorkflowStep(TypedDict, total=False):
    key: str | None
    instruction: str
    validator: ValidatorFn

__all__ = ["WorkflowStep", "ValidatorFn"]
