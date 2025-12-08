from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    openai_model_name: str
    openai_temperature: float
    debug: bool


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    debug = os.getenv("DEBUG", "true").lower()
    return Settings(
        openai_model_name=os.getenv("OPENAI_MODEL_NAME"),
        openai_temperature=float(os.getenv("OPENAI_TEMPERATURE")),
        debug=debug,
    )
