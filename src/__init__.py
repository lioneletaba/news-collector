"""News Automation package."""

from .models.database import create_db_and_tables
from .services.news_service import NewsService

__version__ = "0.1.0"
__all__ = ["create_db_and_tables", "NewsService"]
