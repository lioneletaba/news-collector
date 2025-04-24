from functools import lru_cache
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import HttpUrl, validator

class Settings(BaseSettings):
    """Application settings."""
    
    # API Keys
    openai_api_key: str
    news_api_key: str
    news_data_api_key: str
    
    # Database
    database_url: str = "sqlite:///./news_automation.db"
    
    # Application
    debug: bool = False
    default_topic: str = "Artificial Intelligence"
    
    # File paths
    base_dir: Path = Path(__file__).parent.parent.parent
    pdf_export_dir: Path = base_dir / "exports"
    
    # API Configuration
    news_api_timeout: int = 10
    newscatcher_timeout: int = 10
    openai_timeout: int = 30
    max_retries: int = 3
    retry_delay: int = 1
    
    # OpenAI Configuration
    openai_model: str = "gpt-4o"
    max_tokens: int = 100
    temperature: float = 0.3
    
    @validator("pdf_export_dir")
    def create_export_dir(cls, v: Path) -> Path:
        """Create PDF export directory if it doesn't exist."""
        v.mkdir(parents=True, exist_ok=True)
        return v
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
