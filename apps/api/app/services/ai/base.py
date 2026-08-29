from abc import ABC, abstractmethod


class AIProvider(ABC):
    name: str

    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError

