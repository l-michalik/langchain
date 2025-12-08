from __future__ import annotations

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field


class ChatLLMResult(BaseModel):
    answer: str


CHAT_PARSER = PydanticOutputParser(pydantic_object=ChatLLMResult)
CHAT_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "Provide helpful answers using the format below. {format_instructions} "
                "Current datetime: {current_datetime} ({timezone}). "
            ),
        ),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{query}"),
    ]
)
