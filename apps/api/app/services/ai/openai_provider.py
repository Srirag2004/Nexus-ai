from openai import AsyncOpenAI

from app.core.config import get_settings
from app.core.exceptions import ProviderConfigurationError
from app.services.ai.base import AIProvider


class OpenAIProvider(AIProvider):
    name = "openai"

    def __init__(self) -> None:
        settings = get_settings()
        if not settings.openai_api_key:
            raise ProviderConfigurationError("OPENAI_API_KEY is required for AI_PROVIDER=openai", 500)
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = await self.client.responses.create(
            model=self.model,
            store=False,
            input=[
                {"role": "system", "content": [{"type": "input_text", "text": system_prompt}]},
                {"role": "user", "content": [{"type": "input_text", "text": user_prompt}]},
            ],
        )
        return response.output_text
