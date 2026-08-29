from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.entities import Memory
from app.schemas.memory import MemoryCreate
from app.utils.text import cosine_similarity, simple_embedding


class MemoryService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_memories(self, user_id: UUID) -> list[Memory]:
        result = await self.db.execute(select(Memory).where(Memory.user_id == user_id).order_by(Memory.created_at.desc()))
        return list(result.scalars())

    async def create_memory(self, user_id: UUID, payload: MemoryCreate) -> Memory:
        memory = Memory(
            user_id=user_id,
            category=payload.category,
            content=payload.content,
            importance=payload.importance,
            embedding=simple_embedding(payload.content),
        )
        self.db.add(memory)
        await self.db.commit()
        await self.db.refresh(memory)
        return memory

    async def delete_memory(self, user_id: UUID, memory_id: UUID) -> None:
        await self.db.execute(delete(Memory).where(Memory.user_id == user_id, Memory.id == memory_id))
        await self.db.commit()

    async def extract_candidate(self, user_id: UUID, message: str) -> Memory | None:
        lowered = message.lower()
        categories = {
            "i prefer": "preference",
            "my goal": "goal",
            "i am learning": "learning",
            "remember that": "profile",
        }
        for phrase, category in categories.items():
            if phrase in lowered:
                return await self.create_memory(
                    user_id,
                    MemoryCreate(category=category, content=message, importance=0.7),
                )
        return None

    async def retrieve_relevant(self, user_id: UUID, query: str, limit: int = 3) -> list[Memory]:
        memories = await self.list_memories(user_id)
        query_embedding = simple_embedding(query)
        ranked = sorted(
            memories,
            key=lambda item: cosine_similarity(item.embedding or [], query_embedding) + item.importance,
            reverse=True,
        )
        now = datetime.now(timezone.utc)
        for memory in ranked[:limit]:
            memory.last_used_at = now
        await self.db.commit()
        return ranked[:limit]

