from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_db
from app.schemas.chat import MessageResponse
from app.schemas.conversation import ConversationCreate, ConversationDetailResponse, ConversationResponse
from app.services.ai.factory import get_ai_provider
from app.services.chat.service import ChatService

router = APIRouter()


@router.get("", response_model=list[ConversationResponse])
async def list_conversations(db: AsyncSession = Depends(get_db)) -> list[ConversationResponse]:
    service = ChatService(db, get_ai_provider())
    conversations = await service.list_conversations(get_settings().default_user_id)
    return [ConversationResponse.model_validate(item, from_attributes=True) for item in conversations]


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(payload: ConversationCreate, db: AsyncSession = Depends(get_db)) -> ConversationResponse:
    service = ChatService(db, get_ai_provider())
    conversation = await service.create_conversation(get_settings().default_user_id, payload.title)
    return ConversationResponse.model_validate(conversation, from_attributes=True)


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(conversation_id: str, db: AsyncSession = Depends(get_db)) -> ConversationDetailResponse:
    service = ChatService(db, get_ai_provider())
    conversation = await service.get_conversation(get_settings().default_user_id, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return ConversationDetailResponse(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=[MessageResponse.model_validate(message, from_attributes=True) for message in conversation.messages],
    )


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(conversation_id: str, db: AsyncSession = Depends(get_db)) -> None:
    service = ChatService(db, get_ai_provider())
    await service.delete_conversation(get_settings().default_user_id, conversation_id)

