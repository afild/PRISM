import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./prism_workforce.db")
    nova_database_url: str = os.getenv("NOVA_DATABASE_URL", "sqlite:///../NOVA/nova_finance.db")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    anthropic_api_key: str | None = os.getenv("ANTHROPIC_API_KEY")
    debug: bool = True
    port: int = 8004

    class Config:
        env_file = ".env"

settings = Settings()
