from __future__ import annotations

from core.memory import get_conversation_store
from .base import ValidatorFn, WorkflowStep

WORKFLOW_INSTRUCTION = "Follow a structured process to gather inputs for creating a project."


def _set_current_session_budget(value: float) -> None:
    store = get_conversation_store()
    session_id = store.get_current_session()
    if session_id is not None:
        store.set_workflow_value(session_id, "project", "budget", float(value))


def get_current_project_budget() -> float | None:
    store = get_conversation_store()
    session_id = store.get_current_session()
    if session_id is None:
        return None
    value = store.get_workflow_value(session_id, "project", "budget")
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def validate_project_budget(budget: float) -> tuple[bool, str | None]:
    try:
        value = float(budget)
    except (TypeError, ValueError):
        return False, "Budget must be a number."

    if value > 1000:
        return False, "Amount is too high"

    _set_current_session_budget(value)
    return True, None


def validate_project_description(description: str) -> tuple[bool, str | None]:
    if not isinstance(description, str):
        return False, "Description must be a string."
    if len(description) < 20:
        return False, "Description must be at least 20 characters long."
    return True, None


WORKFLOW_STEPS: list[WorkflowStep] = [
    WorkflowStep(
        key="budget",
        instruction="Ask user what is project budget",
        validator=validate_project_budget,
    ),
    WorkflowStep(
        key="deadline",
        instruction="Ask user what is project description",
        validator=validate_project_description,
    ),
]
