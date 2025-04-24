from datetime import datetime
from typing import List, Optional
from newscatcher import Newscatcher
from pydantic import HttpUrl
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger

from src.collectors.base import ArticleCollectorInterface
from src.models.article import ArticleCreate
from src.utils.config import get_settings
from src.utils.exceptions import ArticleCollectionError

settings = get_settings()

class NewscatcherCollector(ArticleCollectorInterface):
    """Newscatcher implementation of article collector."""
    
    @retry(
        stop=stop_after_attempt(settings.max_retries),
        wait=wait_exponential(multiplier=settings.retry_delay),
        reraise=True
    )
    async def get_articles(
        self,
        source: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[ArticleCreate]:
        """
        Get articles using Newscatcher.
        
        Args:
            source: Domain name of the news source
            start_date: Start date for article search
            end_date: End date for article search
            
        Returns:
            List of ArticleCreate objects
            
        Raises:
            ArticleCollectionError: If article collection fails
        """
        try:
            # Initialize Newscatcher for the website
            nc = Newscatcher(website=f"https://{source}")
            
            # Get articles from RSS feed
            articles_raw = nc.get_news()
            if not articles_raw:
                raise ArticleCollectionError(f"No RSS feed found for {source}")
            
            # Process and filter articles
            articles = []
            for article in articles_raw:
                try:
                    # Parse publication date
                    pub_date = datetime.fromisoformat(
                        article['published'].replace('Z', '+00:00')
                    )
                    
                    # Filter by date range if specified
                    if start_date and pub_date < start_date:
                        continue
                    if end_date and pub_date > end_date:
                        continue
                    
                    articles.append(
                        ArticleCreate(
                            title=article['title'],
                            url=HttpUrl(article['link']),
                            publication_date=pub_date,
                            source=source,
                            content=article.get('summary', ''),
                        )
                    )
                except Exception as e:
                    logger.warning(f"Failed to process article: {e}")
                    continue
            
            logger.info(f"Successfully collected {len(articles)} articles from Newscatcher")
            return articles
            
        except Exception as e:
            logger.error(f"Newscatcher collection failed: {e}")
            raise ArticleCollectionError(
                "Failed to collect articles from Newscatcher"
            ) from e
