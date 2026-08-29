from app.services.ai.base import AIProvider


class MockAIProvider(AIProvider):
    name = "mock"

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        question = user_prompt.split("\n", 1)[0].strip()
        if question.lower() in {"hi", "hello", "hey"}:
            return "Hey, welcome to Nexus. Tell me what you are building, learning, or deciding, and I will help you turn it into a clear next step."
        return (
            f"I have captured your question: \"{question[:180]}\".\n\n"
            "Right now Nexus is running in local preview mode, so your workspace and history are working but a live AI model is not connected yet. "
            "Add an OpenAI API key when you are ready for tailored, model-generated answers."
        )
