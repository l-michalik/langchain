from __future__ import annotations

from .base import WorkflowStep

WORKFLOW_INSTRUCTION = "Behave as a basic, neutral conversational agent."


WORKFLOW_STEPS: list[WorkflowStep] = [
    WorkflowStep(
        key="default_conversation",
        instruction="Ask user what he want to do.",
    )
]
