from __future__ import annotations

from .base import ValidatorFn, WorkflowStep

WORKFLOW_INSTRUCTION = "Follow a structured process to gather inputs for creating a project."


def validate_project_budget(budget: float) -> tuple[bool, str | None]:
    try:
        value = float(budget)
    except (TypeError, ValueError):
        return False, "Budget must be a number."

    if value > 1000:
        return False, "Amount is too high"
    return True, None


WORKFLOW_STEPS: list[WorkflowStep] = [
    WorkflowStep(
        key="plan_project",
        instruction="Ask user what is project budget",
        validator=validate_project_budget,
    )
]
