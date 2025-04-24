from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from src.models.article import ArticleCreate

class ArticleCollectorInterface(ABC):
    """Base interface for article collectors."""
    
    @abstractmethod
    async def get_articles(
        self,
        source: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[ArticleCreate]:
        """Get articles from the source."""
        pass
