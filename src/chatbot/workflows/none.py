from __future__ import annotations

from .base import WorkflowStep

WORKFLOW_INSTRUCTION = "Behave as a conversational agent. Respond to user questions and try to understand the user's intent. Ask questions to determine the action the user wants to perform."

WORKFLOW_STEPS: list[WorkflowStep] = [
    WorkflowStep(
        instruction="Respond to user questions and understand the user's intent. Ask clarifying questions to determine the action the user wants to perform."
    )
]
