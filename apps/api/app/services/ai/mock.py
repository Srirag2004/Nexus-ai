from app.services.ai.base import AIProvider


class MockAIProvider(AIProvider):
    name = "mock"

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        return (
            "Mock NEXUS response:\n"
            f"- intent: {user_prompt[:120]}\n"
            "- grounded_context: mock mode is active, so no external model call was made.\n"
            "- next_step: configure OPENAI_API_KEY and AI_PROVIDER=openai to enable live responses."
        )

