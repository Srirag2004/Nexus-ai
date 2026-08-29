from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_db
from app.schemas.memory import MemoryCreate, MemoryResponse
from app.services.memory.service import MemoryService

router = APIRouter()


@router.get("", response_model=list[MemoryResponse])
async def list_memories(db: AsyncSession = Depends(get_db)) -> list[MemoryResponse]:
    service = MemoryService(db)
    memories = await service.list_memories(get_settings().default_user_id)
    return [MemoryResponse.model_validate(memory, from_attributes=True) for memory in memories]


@router.post("", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
async def create_memory(payload: MemoryCreate, db: AsyncSession = Depends(get_db)) -> MemoryResponse:
    service = MemoryService(db)
    memory = await service.create_memory(get_settings().default_user_id, payload)
    return MemoryResponse.model_validate(memory, from_attributes=True)


@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(memory_id: str, db: AsyncSession = Depends(get_db)) -> None:
    service = MemoryService(db)
    await service.delete_memory(get_settings().default_user_id, memory_id)

