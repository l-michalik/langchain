from __future__ import annotations

from typing import Any

from langchain_core.exceptions import OutputParserException
from langchain_core.messages import AIMessage, HumanMessage

from chains.chat import CHAT_PARSER, CHAT_PROMPT, ChatLLMResult
from core.memory import get_conversation_store
from schemas.chat import ChatRequest, ChatResponse
from utils.datetime import now_iso_in_timezone
from workflows import (
    get_chat_graph,
    get_workflow_instruction,
    get_workflow_step_instruction,
    get_workflow_step_field,
    get_workflow_step_validator,
)


async def handle_chat(chat_request: ChatRequest) -> ChatResponse:
    store = get_conversation_store()
    session_id = chat_request.session_id
    store.set_current_session(session_id)

    previous_workflow = store.get_active_workflow(session_id)
    prompt_messages = await prepare_prompt_messages(store, session_id, chat_request)
    llm_result = await generate_response(prompt_messages)
    current_workflow = store.get_active_workflow(session_id)

    validator = get_workflow_step_validator(current_workflow)
    workflow_changed = previous_workflow != current_workflow
    should_validate = not workflow_changed and validator is not None

    if should_validate:
        validation_input = llm_result.validator_value
        if validation_input is None:
            # LLM did not extract a structured value; fall back to raw user input.
            validation_input = chat_request.query
        is_valid, error_msg = await validate_workflow_step(store, session_id, validation_input)
    else:
        is_valid, error_msg = True, None

    if not is_valid:
        answer_text = await respond_with_validation_error(prompt_messages, error_msg)
    else:
        # After successful validation, refresh prompt for the next step (if any) so the LLM follows the new instruction.
        next_step_instruction = get_workflow_step_instruction(current_workflow)
        if should_validate and next_step_instruction:
            followup_messages = await prepare_prompt_messages(
                store,
                session_id,
                chat_request,
                query_override="Proceed to the next workflow step and prompt the user accordingly.",
            )
            followup_result = await generate_response(followup_messages)
            answer_text = followup_result.answer
        else:
            answer_text = llm_result.answer

    store.append(
        session_id,
        HumanMessage(content=chat_request.query),
        AIMessage(content=answer_text),
    )

    return ChatResponse(answer=answer_text)


async def validate_workflow_step(store, session_id: str, value: Any) -> tuple[bool, str | None]:
    active_workflow = store.get_active_workflow(session_id)
    validator = get_workflow_step_validator(active_workflow)

    if validator is not None:
        is_valid, error_msg = validator(value)
        if not is_valid:
            return False, error_msg or "Input is not valid for this step."
        store.advance_workflow_step(session_id)

    return True, None


async def prepare_prompt_messages(
    store,
    session_id: str,
    chat_request: ChatRequest,
    query_override: str | None = None,
) -> list:
    session_history = store.read(session_id)
    active_workflow = store.get_active_workflow(session_id)

    workflow_instruction = get_workflow_instruction(active_workflow)
    workflow_step_instruction = get_workflow_step_instruction(active_workflow)
    step_field_name, step_field_type = get_workflow_step_field(active_workflow)

    current_datetime, normalized_timezone = now_iso_in_timezone(chat_request.timezone)
    query_text = query_override if query_override is not None else chat_request.query

    return CHAT_PROMPT.format_messages(
        query=query_text,
        history=session_history,
        format_instructions=CHAT_PARSER.get_format_instructions(),
        current_datetime=current_datetime,
        timezone=normalized_timezone,
        active_workflow=active_workflow,
        workflow_instruction=workflow_instruction,
        workflow_step_instruction=workflow_step_instruction,
        workflow_step_field=step_field_name or "none",
        workflow_step_field_type=step_field_type or "unknown",
    )


async def generate_response(prompt_messages: list) -> ChatLLMResult:
    graph = get_chat_graph()
    result_state = await graph.ainvoke({"messages": prompt_messages})
    final_message = result_state["messages"][-1]

    try:
        structured = await CHAT_PARSER.ainvoke(final_message)
        return structured
    except OutputParserException:
        content = final_message.content
        answer = content if isinstance(content, str) else str(content)
        return ChatLLMResult(answer=answer, validator_value=None)


async def respond_with_validation_error(prompt_messages: list, error_msg: str | None) -> str:
    error_text = error_msg or "Input is not valid for this step."
    messages = prompt_messages + [
        HumanMessage(
            content=(
                f"The provided input failed validation: {error_text}. "
                "Explain the issue shortly and guide the user to provide a corrected response."
            )
        )
    ]
    structured = await generate_response(messages)
    return structured.answer
