from __future__ import annotations

from core.logging import get_logger
from core.constants import COLORS

def create_brief():
    """Creates a brief."""
    logger = get_logger(name="CREATE_BRIEF", color=COLORS.get("GREEN", "default"))
    
    logger.debug("Creating a new brief.")
    
    return {
        record_id: "brief_12345",
    }
