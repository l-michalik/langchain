from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict, Literal

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from chains.chat import CHAT_PROMPT
from clients.llm import get_chat_llm
from core.logging import BLUE, get_logger
from core.memory import get_conversation_store
from tools.datetime import relative_date_tool
from tools.workflow import set_active_workflow_tool
from .base import ValidatorFn
from . import brief as _brief_workflow
from . import none as _none_workflow
from . import project as _project_workflow

logger = get_logger("PROMPT", BLUE)


WorkflowName = Literal["none", "brief", "project"]


def get_workflow_instruction(workflow: WorkflowName) -> str:
    if workflow == "brief":
        return _brief_workflow.WORKFLOW_INSTRUCTION.strip()
    if workflow == "project":
        return _project_workflow.WORKFLOW_INSTRUCTION.strip()
    return _none_workflow.WORKFLOW_INSTRUCTION.strip()


def get_workflow_step_instruction(workflow: WorkflowName) -> str:
    """Return the instruction for the current step of the active workflow."""
    store = get_conversation_store()
    session_id = store.get_current_session()
    step_index = 0
    if session_id is not None:
        step_index = store.get_workflow_step_index(session_id)

    raw: list[Any]
    if workflow == "brief":
        raw = getattr(_brief_workflow, "WORKFLOW_STEPS", [])
    elif workflow == "project":
        raw = getattr(_project_workflow, "WORKFLOW_STEPS", [])
    else:
        raw = getattr(_none_workflow, "WORKFLOW_STEPS", [])

    if not raw or step_index < 0 or step_index >= len(raw):
        return ""

    step: Any = raw[step_index]
    if hasattr(step, "get"):
        instruction = step.get("instruction")
        validator = step.get("validator")
    else:
        instruction = getattr(step, "instruction", None)
        validator = getattr(step, "validator", None)

    if instruction is None:
        return ""

    base_instruction = str(instruction).strip()
    validator_text = _get_validator_description(validator)
    if validator_text:
        return f"{base_instruction}\n\nVALIDATION RULES:\n{validator_text}"

    return base_instruction


def _get_validator_description(validator: Any) -> str:
    """Extract a human-readable description from a validator.

    - If it's a callable, use its docstring (if present).
    - If it's a string, return it as-is.
    """
    if validator is None:
        return ""
    if callable(validator):
        doc = getattr(validator, "__doc__", None)
        if isinstance(doc, str):
            return doc.strip()
        return ""
    if isinstance(validator, str):
        return validator.strip()
    return ""


def get_workflow_step_validator(workflow: WorkflowName) -> ValidatorFn | None:
    """Return the Python validator function for the current workflow step, if any."""
    store = get_conversation_store()
    session_id = store.get_current_session()
    step_index = 0
    if session_id is not None:
        step_index = store.get_workflow_step_index(session_id)

    raw: list[Any]
    if workflow == "brief":
        raw = getattr(_brief_workflow, "WORKFLOW_STEPS", [])
    elif workflow == "project":
        raw = getattr(_project_workflow, "WORKFLOW_STEPS", [])
    else:
        raw = getattr(_none_workflow, "WORKFLOW_STEPS", [])

    if not raw or step_index < 0 or step_index >= len(raw):
        return None

    step: Any = raw[step_index]
    if hasattr(step, "get"):
        validator = step.get("validator")
    else:
        validator = getattr(step, "validator", None)

    if callable(validator):
        return validator
    return None


def _prompt_without_history(messages: list[BaseMessage]) -> str:
    system_msg: BaseMessage | None = None
    last_human: BaseMessage | None = None

    for message in messages:
        msg_type = getattr(message, "type", "")
        if msg_type == "system" and system_msg is None:
            system_msg = message
        if msg_type == "human":
            last_human = message

    parts: list[str] = []
    if system_msg is not None:
        parts.append(f"SYSTEM:\n{system_msg.content}")
    if last_human is not None:
        parts.append(f"USER: {last_human.content}")

    return "\n\n".join(parts)


def _build_chat_graph(llm: BaseChatModel):
    tools = [relative_date_tool, set_active_workflow_tool]
    tool_node = ToolNode(tools)
    llm_with_tools = llm.bind_tools(tools)

    def _refresh_system_workflow_instruction(messages: list[BaseMessage]) -> None:
        """Update system message with the latest workflow instruction."""
        store = get_conversation_store()
        session_id = store.get_current_session()
        if session_id is None:
            return

        active_workflow: WorkflowName = store.get_active_workflow(session_id)
        workflow_instruction = get_workflow_instruction(active_workflow)
        workflow_step_instruction = get_workflow_step_instruction(active_workflow)

        marker = "WORKFLOW INSTRUCTION:"
        step_marker = "WORKFLOW STEP INSTRUCTION:"
        for message in messages:
            msg_type = getattr(message, "type", "")
            if msg_type != "system":
                continue
            content = getattr(message, "content", "")
            if not isinstance(content, str) or marker not in content:
                continue

            try:
                prefix, _ = content.split(marker, 1)
            except ValueError:
                continue

            new_block = (
                f"{marker}\n{workflow_instruction}\n\n"
                f"{step_marker}\n{workflow_step_instruction}"
            )
            message.content = f"{prefix}{new_block}"
            break

    async def call_model(state: MessagesState) -> Dict[str, Any]:
        messages: list[BaseMessage] = state["messages"]  # type: ignore[assignment]
        _refresh_system_workflow_instruction(messages)
        logger.debug("%s", _prompt_without_history(messages))
        response = await llm_with_tools.ainvoke(state["messages"])
        return {"messages": [response]}

    def should_continue(state: MessagesState) -> str:
        last_message = state["messages"][-1]
        tool_calls = getattr(last_message, "tool_calls", None)
        if tool_calls:
            return "tools"
        return "end"

    workflow = StateGraph(MessagesState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)

    workflow.set_entry_point("agent")
    workflow.add_edge("tools", "agent")
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {"tools": "tools", "end": END},
    )

    return workflow.compile()


@lru_cache(maxsize=1)
def get_chat_graph():
    llm = get_chat_llm()
    return _build_chat_graph(llm)


__all__ = [
    "get_chat_graph",
    "CHAT_PROMPT",
    "get_workflow_instruction",
    "get_workflow_step_instruction",
    "get_workflow_step_validator",
]
