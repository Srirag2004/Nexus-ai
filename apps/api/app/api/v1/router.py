from fastapi import APIRouter

from app.api.v1.endpoints import agents, auth, career, chat, conversations, documents, evaluations, github, health, memory

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(health.router, tags=["health"])
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(memory.router, prefix="/memories", tags=["memories"])
api_router.include_router(github.router, prefix="/github", tags=["github"])
api_router.include_router(career.router, prefix="/career", tags=["career"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(evaluations.router, prefix="/evaluations", tags=["evaluations"])
