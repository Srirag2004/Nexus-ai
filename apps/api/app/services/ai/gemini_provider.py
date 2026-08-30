import httpx

from app.core.config import get_settings
from app.core.exceptions import NexusError, ProviderConfigurationError
from app.services.ai.base import AIProvider


class GeminiProvider(AIProvider):
    """Gemini Developer API adapter kept server-side with the other providers."""

    name = "gemini"

    def __init__(self) -> None:
        settings = get_settings()
        if not settings.gemini_api_key:
            raise ProviderConfigurationError("GEMINI_API_KEY is required for AI_PROVIDER=gemini", 500)
        self.api_key = settings.gemini_api_key
        self.model = settings.gemini_model

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"{system_prompt}\n\nUser message:\n{user_prompt}",
                        }
                    ]
                }
            ]
        }
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(
                url,
                headers={"x-goog-api-key": self.api_key},
                json=payload,
            )

        if response.status_code == 429:
            raise NexusError("Gemini has reached its current quota. Please wait and try again.", 429)
        if response.is_error:
            raise NexusError("Gemini could not complete this request. Please try again shortly.", 502)

        data = response.json()
        try:
            parts = data["candidates"][0]["content"]["parts"]
            text = "".join(part.get("text", "") for part in parts).strip()
        except (IndexError, KeyError, TypeError) as exc:
            raise NexusError("Gemini returned an empty response. Please try again.", 502) from exc

        if not text:
            raise NexusError("Gemini returned an empty response. Please try again.", 502)
        return text
