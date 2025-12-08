from __future__ import annotations

from typing import Literal

from langchain_core.tools import tool

from core.logging import get_logger
from core.memory import get_conversation_store
from schemas.tools import SetActiveWorkflowInput
from core.logging import YELLOW

@tool("set_active_workflow", args_schema=SetActiveWorkflowInput)
def set_active_workflow_tool(workflow: Literal["none", "brief", "project"]) -> str:
    """
    Set the active workflow for a chat session.

    Use this tool to switch the current conversation mode between:
    - 'none'    – default behaviour
    - 'brief'   – use when the user says they want to create a brief, work on a brief,
                  or otherwise indicates that the goal is to create or refine a brief.
    - 'project' – use when the user says they want to create a project, start a project,
                  or otherwise indicates that the goal is to define or manage a project.

    When the user explicitly mentions they want to create a brief,
    call this tool with workflow='brief' before answering.
    When the user explicitly mentions they want to create a project,
    call this tool with workflow='project' before answering.
    """
    logger = get_logger("SET_ACTIVE_WORKFLOW_TOOL", YELLOW)
    store = get_conversation_store()
    session_id = store.get_current_session()
    if session_id is None:
        return "No active session; cannot set workflow."
    store.set_active_workflow(session_id, workflow)
    logger.debug(f"Active workflow for current session set to '{workflow}'.")
    return f"Active workflow set to '{workflow}' for the current session."
