from __future__ import annotations

from core.logging import get_logger
from core.constants import COLORS

def create_project() -> bool:
    """Creates a project and logs the process."""
    logger = get_logger(name="CREATE_PROJECT", color=COLORS.get("GREEN", "default"))
    
    logger.debug("Creating a new project.")
    
    return True
