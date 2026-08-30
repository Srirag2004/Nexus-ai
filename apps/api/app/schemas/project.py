from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    goal: str = Field(min_length=5, max_length=4000)
    description: str = Field(default="", max_length=8000)
    repository_id: UUID | None = None
    document_ids: list[UUID] = Field(default_factory=list, max_length=10)


class ProjectResponse(BaseModel):
    id: UUID
    title: str
    goal: str
    description: str
    status: str
    repository_id: UUID | None
    repository_name: str | None = None
    document_ids: list[UUID] = Field(default_factory=list)
    document_names: list[str] = Field(default_factory=list)
    brief: str
    milestones: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
