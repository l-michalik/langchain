from __future__ import annotations

from typing import Dict, List, Literal

from langchain_core.messages import BaseMessage


class ConversationStore:
    def __init__(self) -> None:
        self._sessions: Dict[str, List[BaseMessage]] = {}
        self._active_workflows: Dict[str, Literal["none", "brief", "project"]] = {}
        self._current_session_id: str | None = None

    def read(self, session_id: str) -> List[BaseMessage]:
        return list(self._sessions.get(session_id, []))

    def append(self, session_id: str, *messages: BaseMessage) -> None:
        self._sessions.setdefault(session_id, []).extend(messages)

    def get_active_workflow(self, session_id: str) -> Literal["none", "brief", "project"]:
        return self._active_workflows.get(session_id, "none")

    def set_active_workflow(self, session_id: str, workflow: Literal["none", "brief", "project"]) -> None:
        self._active_workflows[session_id] = workflow

    def set_current_session(self, session_id: str) -> None:
        self._current_session_id = session_id

    def get_current_session(self) -> str | None:
        return self._current_session_id


_store: ConversationStore | None = None


def get_conversation_store() -> ConversationStore:
    global _store
    if _store is None:
        _store = ConversationStore()
    return _store
