from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    conversation_id: UUID | None = None
    use_documents: bool = True
    use_memories: bool = True


class MessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    created_at: datetime
    sources: list[dict] = Field(default_factory=list)


class ChatResponse(BaseModel):
    conversation_id: UUID
    reply: MessageResponse
    provider: str
    citations: list[dict] = Field(default_factory=list)

