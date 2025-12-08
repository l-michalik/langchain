from __future__ import annotations

from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str
    session_id: str
    timezone: str
    user_mail: str
    message_files: str


class ChatResponse(BaseModel):
    answer: str
