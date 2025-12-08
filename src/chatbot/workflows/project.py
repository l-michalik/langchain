from __future__ import annotations

from core.memory import get_conversation_store
from .base import ValidatorFn, WorkflowStep

WORKFLOW_INSTRUCTION = "Follow a structured process to gather inputs for creating a project."


def _set_workflow_value(key: str, subkey: str, value: any) -> None:
    """Helper function to set a workflow value in the conversation store."""
    store = get_conversation_store()
    session_id = store.get_current_session()
    if session_id is not None:
        store.set_workflow_value(session_id, key, subkey, value)


def validate_project_budget(budget: float) -> tuple[bool, str | None]:
    text = str(budget)
    num_str = ""
    for ch in text:
        if ch.isdigit() or (ch == "." and "." not in num_str):
            num_str += ch
        elif num_str:
            break

    if not num_str:
        return False, "Budget must be a number."

    try:
        value = float(num_str)
    except (TypeError, ValueError):
        return False, "Budget must be a number."

    if value > 1000:
        return False, "Amount is too high"

    _set_workflow_value("project", "budget", value)
    return True, None


def validate_project_description(description: str) -> tuple[bool, str | None]:
    if not isinstance(description, str):
        return False, "Description must be a string."
    if len(description) < 20:
        return False, "Description must be at least 20 characters long."

    _set_workflow_value("project", "description", description)
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
