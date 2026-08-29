from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.models.entities import User
from app.db.session import get_db
from app.schemas.chat import ChatRequest, ChatResponse, MessageResponse
from app.services.ai.factory import get_ai_provider
from app.services.chat.service import ChatService

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def create_chat(payload: ChatRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)) -> ChatResponse:
    service = ChatService(db, get_ai_provider())
    conversation, reply, provider_name, sources = await service.chat(str(user.id), payload)
    return ChatResponse(
        conversation_id=conversation.id,
        reply=MessageResponse.model_validate(reply, from_attributes=True),
        provider=provider_name,
        citations=sources,
    )
