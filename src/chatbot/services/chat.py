from __future__ import annotations

from typing import Iterable, List

from langchain_core.exceptions import OutputParserException
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

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

    session_history = store.read(session_id)
    active_workflow = store.get_active_workflow(session_id)

    validator = get_workflow_step_validator(active_workflow)
    if validator is not None:
        is_valid, error_msg = validator(chat_request.query)
        if not is_valid:
            answer_text = error_msg or "Input is not valid for this step."
            store.append(
                session_id,
                HumanMessage(content=chat_request.query),
                AIMessage(content=answer_text),
            )
            return ChatResponse(answer=answer_text)
        store.advance_workflow_step(session_id)

    workflow_instruction = get_workflow_instruction(active_workflow)
    workflow_step_instruction = get_workflow_step_instruction(active_workflow)

    current_datetime, normalized_timezone = now_iso_in_timezone(
        chat_request.timezone
    )

    prompt_messages = CHAT_PROMPT.format_messages(
        query=chat_request.query,
        history=session_history,
        format_instructions=CHAT_PARSER.get_format_instructions(),
        current_datetime=current_datetime,
        timezone=normalized_timezone,
        active_workflow=active_workflow,
        workflow_instruction=workflow_instruction,
        workflow_step_instruction=workflow_step_instruction,
    )
    graph = get_chat_graph()
    result_state = await graph.ainvoke({"messages": prompt_messages})
    final_message = result_state["messages"][-1]
    try:
        structured = await CHAT_PARSER.ainvoke(final_message)
        answer_text = structured.answer
    except OutputParserException:
        content = final_message.content
        answer_text = content if isinstance(content, str) else str(content)

    store.append(
        session_id,
        HumanMessage(content=chat_request.query),
        AIMessage(content=answer_text),
    )

    return ChatResponse(answer=answer_text)
