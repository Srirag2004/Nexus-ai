from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_db
from app.schemas.chat import ChatRequest, ChatResponse, MessageResponse
from app.services.ai.factory import get_ai_provider
from app.services.chat.service import ChatService

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def create_chat(payload: ChatRequest, db: AsyncSession = Depends(get_db)) -> ChatResponse:
    service = ChatService(db, get_ai_provider())
    conversation, reply, provider_name, sources = await service.chat(get_settings().default_user_id, payload)
    return ChatResponse(
        conversation_id=conversation.id,
        reply=MessageResponse.model_validate(reply, from_attributes=True),
        provider=provider_name,
        citations=sources,
    )

