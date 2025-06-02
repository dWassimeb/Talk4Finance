# backend/app/core/config.py
"""
Application configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App settings
    app_name: str = "PowerBI Agent"
    debug: bool = True

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Database
    database_url: str = "sqlite:///./powerbi_agent.db"

    # PowerBI settings (from your config)
    powerbi_dataset_id: str = "b715c872-443b-42a7-b5d0-4cc9f92bd88b"
    powerbi_workspace_id: str = "7ab6eef2-3720-409f-9dee-d5cd868c559e"

    # OpenAI/Custom LLM
    gpt_api_key: str = "2b24fef721d14c94a333ab2e4f686f40"

    class Config:
        env_file = ".env"

settings = Settings()