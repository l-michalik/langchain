from __future__ import annotations

from typing import Literal

from langchain_core.tools import tool
from core.logging import get_logger
from core.memory import get_conversation_store
from schemas.tools import SetActiveWorkflowInput
from core.constants import COLORS


@tool("set_active_workflow", args_schema=SetActiveWorkflowInput)
def set_active_workflow_tool(workflow: Literal["none", "brief", "project"]) -> str:
    """
    Execute this tool only when user explicitly requests to change the active workflow.
    If user say "create a brief/project", this tool should be triggered.
    """
    logger = _get_logger()
    store = get_conversation_store()
    session_id = store.get_current_session()

    if not session_id:
        return "No active session; cannot set workflow."

    store.set_active_workflow(session_id, workflow)
    logger.debug(f"Active workflow for current session set to '{workflow}'.")
    return f"Active workflow set to '{workflow}' for the current session."


def _get_logger():
    """Helper to initialize the logger."""
    return get_logger("SET_ACTIVE_WORKFLOW_TOOL", COLORS["YELLOW"])
