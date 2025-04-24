from datetime import datetime
from typing import List, Optional
from newsapi import NewsApiClient
from pydantic import HttpUrl
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger

from src.collectors.base import ArticleCollectorInterface
from src.models.article import ArticleCreate
from src.utils.config import get_settings
from src.utils.exceptions import ArticleCollectionError

settings = get_settings()

class NewsAPICollector(ArticleCollectorInterface):
    """NewsAPI implementation of article collector."""
    
    def __init__(self):
        """Initialize NewsAPI client."""
        try:
            self.client = NewsApiClient(api_key=settings.news_api_key)
        except Exception as e:
            logger.error(f"Failed to initialize NewsAPI client: {e}")
            raise ArticleCollectionError("NewsAPI initialization failed") from e
    

    
    def _generate_default_date_range(self) -> tuple[datetime, datetime]:
        """Generate default date range for yesterday."""
        end_date = datetime.utcnow()
        start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
        return start_date, end_date
    


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
        Get articles from NewsAPI.
        
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
            # Format dates for NewsAPI (must be YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
            from_param = start_date.strftime('%Y-%m-%dT%H:%M:%S') if start_date else None
            to_param = end_date.strftime('%Y-%m-%dT%H:%M:%S') if end_date else None
            
            # Get articles from NewsAPI
            response = self.client.get_everything(
                domains=source,
                from_param=from_param,
                to=to_param,
                language='en',
                sort_by='publishedAt'
            )
            
            if response['status'] != 'ok':
                raise ArticleCollectionError(
                    f"NewsAPI error: {response.get('message', 'Unknown error')}"
                )
            
            # Convert response to ArticleCreate objects
            articles = []
            for article in response['articles']:
                try:
                    articles.append(
                        ArticleCreate(
                            title=article['title'],
                            url=HttpUrl(article['url']),
                            publication_date=datetime.fromisoformat(
                                article['publishedAt'].replace('Z', '+00:00')
                            ),
                            source=source,
                            content=article.get('content', article.get('description', '')),
                        )
                    )
                except Exception as e:
                    logger.warning(f"Failed to process article: {e}")
                    continue
            
            logger.info(f"Successfully collected {len(articles)} articles from NewsAPI")
            return articles
            
        except Exception as e:
            logger.error(f"NewsAPI collection failed: {e}")
            raise ArticleCollectionError("Failed to collect articles from NewsAPI") from e
