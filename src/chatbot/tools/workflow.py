from __future__ import annotations

from typing import Literal

from langchain_core.tools import tool

from core.logging import get_logger
from core.memory import get_conversation_store
from schemas.tools import SetActiveWorkflowInput


@tool("set_active_workflow", args_schema=SetActiveWorkflowInput)
def set_active_workflow_tool(workflow: Literal["none", "brief", "project"]) -> str:
    """
    Set the active workflow for a chat session.

    Use this to switch the current conversation mode between:
    - 'none'   – default behaviour
    - 'brief'  – short, concise answers
    - 'project' – more detailed, project-oriented assistance
    """
    logger = get_logger("chatbot.tools.workflow")
    logger.debug("Invoked with workflow=%s", workflow)
    store = get_conversation_store()
    session_id = store.get_current_session()
    if session_id is None:
        return "No active session; cannot set workflow."
    store.set_active_workflow(session_id, workflow)
    return f"Active workflow for current session set to '{workflow}'."
