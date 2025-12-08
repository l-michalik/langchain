from __future__ import annotations

from .base import WorkflowStep

WORKFLOW_INSTRUCTION = "Follow a structured process to gather inputs for creating a brief."


WORKFLOW_STEPS: list[WorkflowStep] = [
    WorkflowStep(
        key="name",
        instruction="Ask user what is his name",
    )
]
