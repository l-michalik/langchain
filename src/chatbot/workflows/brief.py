from __future__ import annotations

from core.memory import get_conversation_store
from .base import WorkflowStep

WORKFLOW_INSTRUCTION = "Follow a structured process to gather inputs for creating a brief."


def _set_brief_value(key: str, value: str) -> None:
    store = get_conversation_store()
    session_id = store.get_current_session()
    if session_id is not None:
        store.set_workflow_value(session_id, "brief", key, value)

WORKFLOW_STEPS: list[WorkflowStep] = [
    WorkflowStep(
        key="work_types",
        instruction="Ask the user what type of work they need (e.g. design, research, engineering).",
    ),
    WorkflowStep(
        key="name",
        instruction="Ask the user for their name.",
    ),
    WorkflowStep(
        key="description",
        instruction="Ask user: 'Please enter a brief description of what needs to be done, including specifications, quantity of items, and any other details that may be required for WAA to execute this brief.'",
    ),
]
