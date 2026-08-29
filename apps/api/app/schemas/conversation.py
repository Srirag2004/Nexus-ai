from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.chat import MessageResponse


class ConversationCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)


class ConversationResponse(BaseModel):
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime


class ConversationDetailResponse(ConversationResponse):
    messages: list[MessageResponse] = Field(default_factory=list)

