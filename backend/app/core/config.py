# backend/app/core/config.py
"""
Configuration settings - Fixed with algorithm setting
"""
import os
from typing import Optional

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings

class Settings(BaseSettings):
    # Database - Fixed path to match your actual database location
    database_url: str = "sqlite:///./powerbi_agent.db"

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"  # Missing algorithm setting
    access_token_expire_minutes: int = 1440  # 24 hours

    # PowerBI Configuration
    powerbi_dataset_id: Optional[str] = None
    powerbi_workspace_id: Optional[str] = None

    # GPT Configuration
    gpt_api_key: Optional[str] = None

    # Email Configuration (SMTP)
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    from_email: str = "noreply@docaposte.fr"

    # Application Configuration
    base_url: str = "http://localhost:3000"

    # Admin Configuration
    admin_email: str = "mohamed-ouassime.el-yamani@docaposte.fr"
    allowed_domains: list = ["@docaposte.fr", "@softeam.fr"]

    # Rate Limiting
    registration_rate_limit: int = 5  # Max registrations per hour per IP
    login_rate_limit: int = 10  # Max login attempts per hour per IP

    class Config:
        env_file = ".env"

settings = Settings()