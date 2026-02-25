# File: app/config.py
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ValidationError


class Settings(BaseSettings):
    GOOGLE_CREDENTIALS_FILE: str
    SPREADSHEET_ID: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

try:
    settings = Settings()
except ValidationError as e:
    print(f"Configuration Error: Missing required environment variables. Details: {e}")
    exit(1)
