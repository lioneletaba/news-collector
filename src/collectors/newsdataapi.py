from datetime import datetime
from typing import List, Optional
from newsdataapi import NewsDataApiClient
from pydantic import HttpUrl
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger

from src.collectors.base import ArticleCollectorInterface
from src.models.article import ArticleCreate
from src.utils.config import get_settings
from src.utils.exceptions import ArticleCollectionError

settings = get_settings()

class NewsDataAPICollector(ArticleCollectorInterface):
    """NewsDataAPI implementation of article collector."""
    def __init__(self):
        try:
            self.client = NewsDataApiClient(apikey=settings.news_api_key)
        except Exception as e:
            logger.error(f"Failed to initialize NewsDataApiClient: {e}")
            raise ArticleCollectionError("NewsDataAPI initialization failed") from e

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
        try:
            # Format dates for NewsDataAPI
            from_param = start_date.strftime('%Y-%m-%d') if start_date else None
            to_param = end_date.strftime('%Y-%m-%d') if end_date else None

            # Get articles from NewsDataAPI
            response = self.client.news_api(
                domain=source,
                from_param=from_param,
                to_param=to_param,
                language='en',
            )

            if response['status'] != 'success':
                raise ArticleCollectionError(
                    f"NewsDataAPI error: {response.get('message', 'Unknown error')}"
                )

            articles = []
            for article in response['results']:
                try:
                    articles.append(
                        ArticleCreate(
                            title=article['title'],
                            url=HttpUrl(article['link']),
                            publication_date=datetime.fromisoformat(article['pubDate'].replace('Z', '+00:00')),
                            source=source,
                            content=article.get('description', ''),
                        )
                    )
                except Exception as e:
                    logger.warning(f"Failed to process article: {e}")
                    continue
            logger.info(f"Successfully collected {len(articles)} articles from NewsDataAPI")
            return articles
        except Exception as e:
            logger.error(f"NewsDataAPI collection failed: {e}")
            raise ArticleCollectionError("Failed to collect articles from NewsDataAPI") from e
