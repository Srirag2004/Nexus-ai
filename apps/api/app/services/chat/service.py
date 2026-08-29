import time
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.graph import run_agent_flow
from app.agents.state import AgentState
from app.db.models.entities import AgentRun, Conversation, Message, User
from app.schemas.chat import ChatRequest
from app.services.ai.base import AIProvider
from app.services.memory.service import MemoryService
from app.services.rag.service import DocumentService


class ChatService:
    def __init__(self, db: AsyncSession, provider: AIProvider) -> None:
        self.db = db
        self.provider = provider
        self.memory_service = MemoryService(db)
        self.document_service = DocumentService(db)

    async def list_conversations(self, user_id: str) -> list[Conversation]:
        result = await self.db.execute(
            select(Conversation).where(Conversation.user_id == uuid.UUID(user_id)).order_by(Conversation.updated_at.desc())
        )
        return list(result.scalars())

    async def get_conversation(self, user_id: str, conversation_id: uuid.UUID) -> Conversation | None:
        result = await self.db.execute(
            select(Conversation).where(
                Conversation.user_id == uuid.UUID(user_id),
                Conversation.id == conversation_id,
            )
        )
        conversation = result.scalar_one_or_none()
        if conversation:
            await self.db.refresh(conversation, ["messages"])
        return conversation

    async def create_conversation(self, user_id: str, title: str) -> Conversation:
        conversation = Conversation(user_id=uuid.UUID(user_id), title=title)
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation

    async def delete_conversation(self, user_id: str, conversation_id: uuid.UUID) -> None:
        conversation = await self.get_conversation(user_id, conversation_id)
        if conversation:
            await self.db.delete(conversation)
            await self.db.commit()

    async def chat(self, user_id: str, payload: ChatRequest) -> tuple[Conversation, Message, str, list[dict[str, Any]]]:
        started = time.perf_counter()
        conversation = await self.get_conversation(user_id, payload.conversation_id) if payload.conversation_id else None
        if conversation is None:
            conversation = await self.create_conversation(user_id, payload.message[:60])

        user_message = Message(conversation_id=conversation.id, role="user", content=payload.message, sources=[])
        self.db.add(user_message)
        await self.db.flush()

        memories = await self.memory_service.retrieve_relevant(uuid.UUID(user_id), payload.message) if payload.use_memories else []
        await self.memory_service.extract_candidate(uuid.UUID(user_id), payload.message)
        rag_result = await self.document_service.ask(uuid.UUID(user_id), payload.message) if payload.use_documents else None

        state = AgentState(
            user_message=payload.message,
            retrieved_documents=rag_result.sources if rag_result else [],
            retrieved_memories=[memory.content for memory in memories],
        )
        state = await run_agent_flow(state)

        system_prompt = (
            "You are NEXUS AI, an engineering workspace assistant. Use provided memory and source context when available. "
            "Be concise, practical, and cite sources when context comes from knowledge documents."
        )
        user_prompt = payload.message
        if memories:
            user_prompt += "\n\nMemories:\n" + "\n".join(f"- {memory.content}" for memory in memories)
        if rag_result and rag_result.sources:
            user_prompt += "\n\nKnowledge snippets:\n" + "\n".join(
                f"- {source['filename']}: {source['snippet']}" for source in rag_result.sources
            )
        user_prompt += "\n\nAgent plan:\n" + "\n".join(f"- {step}" for step in state.plan)

        assistant_content = await self.provider.generate(system_prompt, user_prompt)
        sources = rag_result.sources if rag_result else []
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=assistant_content,
            sources=sources,
        )
        self.db.add(assistant_message)
        self.db.add(
            AgentRun(
                user_id=uuid.UUID(user_id),
                conversation_id=conversation.id,
                agent_name="nexus-orchestrator",
                status="completed",
                input_summary=payload.message[:200],
                output_summary=assistant_content[:200],
                duration_ms=int((time.perf_counter() - started) * 1000),
            )
        )
        await self.db.commit()
        await self.db.refresh(assistant_message)
        return conversation, assistant_message, self.provider.name, sources
