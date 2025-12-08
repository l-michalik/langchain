from __future__ import annotations

from typing import Optional

from langchain_openai import ChatOpenAI

from core.config import get_settings

_llm: Optional[ChatOpenAI] = None


def get_chat_llm() -> ChatOpenAI:
    global _llm
    if _llm is None:
        settings = get_settings()
        _llm = ChatOpenAI(model=settings.openai_model_name, temperature=settings.openai_temperature)
    return _llm
