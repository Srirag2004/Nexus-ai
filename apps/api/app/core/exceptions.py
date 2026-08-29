class NexusError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ProviderConfigurationError(NexusError):
    pass


class NotFoundError(NexusError):
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=404)

