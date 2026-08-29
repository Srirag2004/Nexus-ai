from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.models.entities import User
from app.db.session import get_db
from app.schemas.memory import MemoryCreate, MemoryResponse
from app.services.memory.service import MemoryService

router = APIRouter()


@router.get("", response_model=list[MemoryResponse])
async def list_memories(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)) -> list[MemoryResponse]:
    service = MemoryService(db)
    memories = await service.list_memories(user.id)
    return [MemoryResponse.model_validate(memory, from_attributes=True) for memory in memories]


@router.post("", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
async def create_memory(payload: MemoryCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)) -> MemoryResponse:
    service = MemoryService(db)
    memory = await service.create_memory(user.id, payload)
    return MemoryResponse.model_validate(memory, from_attributes=True)


@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(memory_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)) -> None:
    service = MemoryService(db)
    await service.delete_memory(user.id, memory_id)
