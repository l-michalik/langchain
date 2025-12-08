from __future__ import annotations

from typing import Tuple

from langchain_core.exceptions import OutputParserException
from langchain_core.messages import AIMessage, HumanMessage

from chains.chat import CHAT_PARSER, CHAT_PROMPT
from core.memory import get_conversation_store
from schemas.chat import ChatRequest, ChatResponse
from utils.datetime import now_iso_in_timezone
from workflows import (
    get_chat_graph,
    get_workflow_instruction,
    get_workflow_step_instruction,
    get_workflow_step_validator,
)


async def handle_chat(chat_request: ChatRequest) -> ChatResponse:
    store = get_conversation_store()
    session_id = chat_request.session_id

    store.set_current_session(session_id)

    if not await validate_workflow_step(store, session_id, chat_request):
        return ChatResponse(answer="Input is not valid for this step.")

    prompt_messages = await prepare_prompt_messages(store, session_id, chat_request)
    answer_text = await generate_response(prompt_messages)

    store.append(
        session_id,
        HumanMessage(content=chat_request.query),
        AIMessage(content=answer_text),
    )

    return ChatResponse(answer=answer_text)


async def validate_workflow_step(store, session_id: str, chat_request: ChatRequest) -> bool:
    active_workflow = store.get_active_workflow(session_id)
    validator = get_workflow_step_validator(active_workflow)

    if validator is not None:
        is_valid, error_msg = validator(chat_request.query)
        if not is_valid:
            store.append(
                session_id,
                HumanMessage(content=chat_request.query),
                AIMessage(content=error_msg or "Input is not valid for this step."),
            )
            return False
        store.advance_workflow_step(session_id)

    return True


async def prepare_prompt_messages(store, session_id: str, chat_request: ChatRequest) -> list:
    session_history = store.read(session_id)
    active_workflow = store.get_active_workflow(session_id)

    workflow_instruction = get_workflow_instruction(active_workflow)
    workflow_step_instruction = get_workflow_step_instruction(active_workflow)

    current_datetime, normalized_timezone = now_iso_in_timezone(chat_request.timezone)

    return CHAT_PROMPT.format_messages(
        query=chat_request.query,
        history=session_history,
        format_instructions=CHAT_PARSER.get_format_instructions(),
        current_datetime=current_datetime,
        timezone=normalized_timezone,
        active_workflow=active_workflow,
        workflow_instruction=workflow_instruction,
        workflow_step_instruction=workflow_step_instruction,
    )


async def generate_response(prompt_messages: list) -> str:
    graph = get_chat_graph()
    result_state = await graph.ainvoke({"messages": prompt_messages})
    final_message = result_state["messages"][-1]

    try:
        structured = await CHAT_PARSER.ainvoke(final_message)
        return structured.answer
    except OutputParserException:
        content = final_message.content
        return content if isinstance(content, str) else str(content)
