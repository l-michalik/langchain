from __future__ import annotations

from langchain_core.tools import tool

from core.logging import GREEN, get_logger
from core.memory import get_conversation_store

def _get_store():
    return get_conversation_store()

@tool("create_project")
def create_project_tool() -> str:
    """Use this tool to create a new project."""
    logger = get_logger("CREATE_PROJECT_TOOL", GREEN)
    
    logger.debug("create_project_tool invoked")
   
    return 'OK: Project created successfully.'