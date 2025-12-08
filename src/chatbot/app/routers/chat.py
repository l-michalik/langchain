from __future__ import annotations

from typing import List

from fastapi import APIRouter, Form, HTTPException

from schemas.chat import ChatRequest, ChatResponse
from services.chat import handle_chat
from core.logging import get_logger

router = APIRouter()

logger = get_logger("chatbot.app.routers")


@router.post("", response_model=ChatResponse)
async def chat_invoke(
    query: str = Form(...),
    session_id: str = Form(...),
    timezone: str = Form(...),
    user_mail: str = Form(None),
    message_files: List[str] = Form(None),
) -> ChatResponse:
    chat_request = ChatRequest(
        query=query,
        session_id=session_id,
        timezone=timezone,
        user_mail=user_mail or "",
        message_files=",".join(message_files) if message_files else "",
    )
    try:
        return await handle_chat(chat_request)
    except Exception as exc:
        logger.error("Error handling chat request: %s", exc, exc_info=True)    
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request. Please try again later.",
        ) from exc
