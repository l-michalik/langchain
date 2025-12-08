from __future__ import annotations

from typing import Any, Dict, List, Literal
from dataclasses import dataclass

from langchain_core.messages import BaseMessage
from core.logging import CYAN, get_logger


@dataclass
class ProjectWorkflowState:
    budget: float | None = None
    description: str | None = None
    step_index: int = 0


class ConversationStore:
    def __init__(self) -> None:
        self._sessions: Dict[str, List[BaseMessage]] = {}
        self._active_workflows: Dict[str, Literal["none", "brief", "project"]] = {}
        self._current_session_id: str | None = None
        self._workflows: Dict[str, Any] = {}
        self._logger = get_logger("WORKFLOW_STATE", CYAN)

    def read(self, session_id: str) -> List[BaseMessage]:
        return list(self._sessions.get(session_id, []))

    def append(self, session_id: str, *messages: BaseMessage) -> None:
        self._sessions.setdefault(session_id, []).extend(messages)

    def get_active_workflow(self, session_id: str) -> Literal["none", "brief", "project"]:
        return self._active_workflows.get(session_id, "none")

    def set_active_workflow(self, session_id: str, workflow: Literal["none", "brief", "project"]) -> None:
        self._active_workflows[session_id] = workflow
        if workflow == "project":
            self.init_project_workflow(session_id)
        else:
            self.set_workflow_step_index(session_id, 0)

    def set_current_session(self, session_id: str) -> None:
        self._current_session_id = session_id

    def get_current_session(self) -> str | None:
        return self._current_session_id

    def init_project_workflow(self, session_id: str) -> None:
        self._workflows["project"] = ProjectWorkflowState()
        self._logger.debug(repr(self._workflows))

    def set_workflow_value(self, session_id: str, workflow: str, key: str, value: Any) -> None:
        if workflow == "project":
            state = self._workflows.get("project")
            if not isinstance(state, ProjectWorkflowState):
                state = ProjectWorkflowState()
                self._workflows["project"] = state
            if hasattr(state, key):
                setattr(state, key, value)
        else:
            workflow_state = self._workflows.setdefault(workflow, {})
            workflow_state[key] = value
        self._logger.debug(repr(self._workflows))

    def get_workflow_value(self, session_id: str, workflow: str, key: str) -> Any | None:
        if workflow == "project":
            state = self._workflows.get("project")
            if isinstance(state, ProjectWorkflowState):
                return getattr(state, key, None)
            return None
        return self._workflows.get(workflow, {}).get(key)

    def get_workflow_step_index(self, session_id: str) -> int:
        workflow = self.get_active_workflow(session_id)
        index = self.get_workflow_value(session_id, workflow, "step_index")
        if index is None:
            return 0
        try:
            return int(index)
        except (TypeError, ValueError):
            return 0

    def set_workflow_step_index(self, session_id: str, index: int) -> None:
        workflow = self.get_active_workflow(session_id)
        if index < 0:
            index = 0
        self.set_workflow_value(session_id, workflow, "step_index", int(index))

    def advance_workflow_step(self, session_id: str) -> None:
        current = self.get_workflow_step_index(session_id)
        self.set_workflow_step_index(session_id, current + 1)


_store: ConversationStore | None = None


def get_conversation_store() -> ConversationStore:
    global _store
    if _store is None:
        _store = ConversationStore()
    return _store
