from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from langchain_core.globals import set_debug

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    openai_model_name: str
    openai_temperature: float
    debug: bool

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    load_dotenv()
    
    set_debug(True)
    
    return Settings(
        openai_model_name=os.getenv("OPENAI_MODEL_NAME"),
        openai_temperature=os.getenv("OPENAI_TEMPERATURE"),
        debug=os.getenv("DEBUG"),
    )
