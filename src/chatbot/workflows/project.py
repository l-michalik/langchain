from __future__ import annotations

from .base import WorkflowStep

WORKFLOW_INSTRUCTION = "Follow a structured process to gather inputs for creating a project."



WORKFLOW_STEPS: list[WorkflowStep] = [
    WorkflowStep(
        key="plan_project",
        instruction="Ask user what is project budget",
    )
]
