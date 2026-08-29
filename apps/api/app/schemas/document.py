from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    content_type: str
    status: str
    created_at: datetime
    metadata: dict = Field(default_factory=dict)


class DocumentAskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    top_k: int = Field(default=4, ge=1, le=10)


class DocumentAskResponse(BaseModel):
    answer: str
    sources: list[dict] = Field(default_factory=list)

