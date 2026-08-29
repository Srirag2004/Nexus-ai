from typing import Any

from pydantic import BaseModel, Field


class AgentState(BaseModel):
    user_message: str
    retrieved_documents: list[dict[str, Any]] = Field(default_factory=list)
    retrieved_memories: list[str] = Field(default_factory=list)
    repository_context: list[dict[str, Any]] = Field(default_factory=list)
    plan: list[str] = Field(default_factory=list)
    final_answer: str = ""

