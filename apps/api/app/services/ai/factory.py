from app.core.config import get_settings
from app.services.ai.base import AIProvider
from app.services.ai.gemini_provider import GeminiProvider
from app.services.ai.mock import MockAIProvider
from app.services.ai.openai_provider import OpenAIProvider


def get_ai_provider() -> AIProvider:
    settings = get_settings()
    if settings.ai_provider == "openai":
        return OpenAIProvider()
    if settings.ai_provider == "gemini":
        return GeminiProvider()
    return MockAIProvider()
