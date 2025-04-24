from datetime import datetime, timedelta
from typing import List, Optional
from loguru import logger

from .base import ArticleCollectorInterface
from .newsapi import NewsAPICollector
from .newsdataapi import NewsDataAPICollector
from src.models.article import ArticleCreate
from src.utils.exceptions import ArticleCollectionError

class ArticleCollector:
    """Main article collector using a pool of collectors."""

    def __init__(self):
        """Initialize a pool of collectors (order matters)."""
        self.collectors = [
            NewsAPICollector(),
            NewsDataAPICollector(),
            # Add more collectors here in the future
        ]

    async def get(
        self,
        source: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[ArticleCreate]:
        """
        Try each collector in order until one returns articles.
        """
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=1)

        last_exception = None
        for collector in self.collectors:
            try:
                articles = await collector.get_articles(
                    source=source,
                    start_date=start_date,
                    end_date=end_date
                )
                if articles:
                    logger.info(f"Successfully retrieved articles from {collector.__class__.__name__}")
                    return articles
            except ArticleCollectionError as e:
                logger.warning(f"{collector.__class__.__name__} failed: {e}")
                last_exception = e
        # If we get here with no articles, raise an error
        raise ArticleCollectionError(
            f"No articles found for {source} between {start_date} and {end_date}. Last error: {last_exception}"
        )
