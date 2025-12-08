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
from . import brief as _brief_workflow
from . import none as _none_workflow
from . import project as _project_workflow

logger = get_logger("PROMPT", BLUE)


WorkflowName = Literal["none", "brief", "project"]


def get_workflow_instruction(workflow: WorkflowName) -> str:
    if workflow == "brief":
        return _brief_workflow.WORKFLOW_INSTRUCTION
    if workflow == "project":
        return _project_workflow.WORKFLOW_INSTRUCTION
    return _none_workflow.WORKFLOW_INSTRUCTION


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

        active_workflow: WorkflowName = store.get_active_workflow(session_id)  # type: ignore[assignment]
        workflow_instruction = get_workflow_instruction(active_workflow)

        marker = "WORKFLOW INSTRUCTIONS:"
        for message in messages:
            msg_type = getattr(message, "type", "")
            if msg_type != "system":
                continue
            content = getattr(message, "content", "")
            if not isinstance(content, str) or marker not in content:
                continue
            prefix, _ = content.split(marker, 1)
            message.content = f"{prefix}{marker} {workflow_instruction}"
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


__all__ = ["get_chat_graph", "CHAT_PROMPT", "get_workflow_instruction"]
