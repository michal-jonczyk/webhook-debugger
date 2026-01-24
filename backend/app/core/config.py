from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "Webhook Debugger"
    APP_VERSION: str = "0.1.0"
    PORT: int = 8000
    BASE_URL: str = "http://localhost:8000"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    ANTHROPIC_API_KEY: str = ""
    AI_ENABLED: bool = True
    AI_CALLS_PER_ENDPOINT_PER_HOUR: int = 10
    AI_CALLS_PER_IP_PER_HOUR: int = 20
    MAX_AI_TOKENS: int = 512

    def get_allowed_origins(self) -> List[str]:
        return self.ALLOWED_ORIGINS.split(",")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()