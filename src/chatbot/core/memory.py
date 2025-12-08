from __future__ import annotations

from typing import Any, Dict, List, Literal
from dataclasses import dataclass

from langchain_core.messages import BaseMessage
from core.logging import get_logger
from core.constants import COLORS, WorkTypes


@dataclass
class ProjectWorkflowState:
    budget: float | None = None
    description: str | None = None
    step_index: int = 0


@dataclass
class BriefWorkflowState:
    work_types: List[WorkTypes] | None = None
    name: str | None = None
    description: str | None = None
    step_index: int = 0


class ConversationStore:
    def __init__(self) -> None:
        self._sessions: Dict[str, List[BaseMessage]] = {}
        self._active_workflows: Dict[str, Literal["none", "brief", "project"]] = {}
        self._current_session_id: str | None = None
        self._workflows: Dict[str, Any] = {}
        self._logger = get_logger("WORKFLOW_STATE", COLORS["CYAN"])

    def read(self, session_id: str) -> List[BaseMessage]:
        return self._sessions.get(session_id, []).copy()

    def append(self, session_id: str, *messages: BaseMessage) -> None:
        self._sessions.setdefault(session_id, []).extend(messages)

    def get_active_workflow(self, session_id: str) -> Literal["none", "brief", "project"]:
        return self._active_workflows.get(session_id, "none")

    def set_active_workflow(self, session_id: str, workflow: Literal["none", "brief", "project"]) -> None:
        self._active_workflows[session_id] = workflow
        if workflow == "project":
            self._initialize_project_workflow(session_id)
        elif workflow == "brief":
            self._initialize_brief_workflow(session_id)
        else:
            self.set_workflow_step_index(session_id, 0)

    def set_current_session(self, session_id: str) -> None:
        self._current_session_id = session_id

    def get_current_session(self) -> str | None:
        return self._current_session_id

    def _initialize_project_workflow(self, session_id: str) -> None:
        self._workflows["project"] = ProjectWorkflowState()
        self._logger.debug(repr(self._workflows))

    def _initialize_brief_workflow(self, session_id: str) -> None:
        self._workflows["brief"] = BriefWorkflowState()
        self._logger.debug(repr(self._workflows))

    def set_workflow_value(self, session_id: str, workflow: str, key: str, value: Any) -> None:
        if workflow == "project":
            self._set_project_workflow_value(key, value)
        elif workflow == "brief":
            self._set_brief_workflow_value(key, value)
        else:
            self._workflows.setdefault(workflow, {})[key] = value
        self._logger.debug(repr(self._workflows))

    def _set_project_workflow_value(self, key: str, value: Any) -> None:
        state = self._workflows.get("project", ProjectWorkflowState())
        if hasattr(state, key):
            setattr(state, key, value)
        self._workflows["project"] = state

    def _set_brief_workflow_value(self, key: str, value: Any) -> None:
        state = self._workflows.get("brief", BriefWorkflowState())
        if hasattr(state, key):
            setattr(state, key, value)
        self._workflows["brief"] = state

    def get_workflow_value(self, session_id: str, workflow: str, key: str) -> Any | None:
        if workflow == "project":
            state = self._workflows.get("project")
            return getattr(state, key, None) if isinstance(state, ProjectWorkflowState) else None
        if workflow == "brief":
            state = self._workflows.get("brief")
            return getattr(state, key, None) if isinstance(state, BriefWorkflowState) else None
        return self._workflows.get(workflow, {}).get(key)

    def get_workflow_step_index(self, session_id: str) -> int:
        workflow = self.get_active_workflow(session_id)
        index = self.get_workflow_value(session_id, workflow, "step_index")
        return self._safe_int(index, default=0)

    def set_workflow_step_index(self, session_id: str, index: int) -> None:
        workflow = self.get_active_workflow(session_id)
        self.set_workflow_value(session_id, workflow, "step_index", max(0, index))

    def advance_workflow_step(self, session_id: str) -> None:
        current = self.get_workflow_step_index(session_id)
        self.set_workflow_step_index(session_id, current + 1)

    @staticmethod
    def _safe_int(value: Any, default: int = 0) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default


_store: ConversationStore | None = None


def get_conversation_store() -> ConversationStore:
    global _store
    if _store is None:
        _store = ConversationStore()
    return _store
