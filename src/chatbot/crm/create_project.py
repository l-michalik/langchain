from __future__ import annotations

from core.logging import GREEN, get_logger

def create_project() -> str:
    logger = get_logger("CREATE_PROJECT", GREEN)
    
    logger.debug("CREATE_PROJECT")
   
    return True