from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class MemoryCreate(BaseModel):
    category: str = Field(min_length=1, max_length=50)
    content: str = Field(min_length=1, max_length=2000)
    importance: float = Field(default=0.5, ge=0, le=1)


class MemoryResponse(BaseModel):
    id: UUID
    category: str
    content: str
    importance: float
    created_at: datetime
    last_used_at: datetime | None = None

