from typing import List
import openai
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger

from src.models.article import ArticleCreate
from src.utils.config import get_settings
from src.utils.exceptions import ArticleFilterError

settings = get_settings()

class ArticleFilter:
    """Filter articles based on topic using OpenAI GPT-4."""
    
    def __init__(self):
        """Initialize OpenAI async client."""
        self.openai_client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
    
    def _create_filter_prompt(self, article: ArticleCreate, topic: str) -> str:
        """Create prompt for OpenAI API."""
        return f"""
        Analyze if the following article is related to the topic: {topic}
        
        Article Title: {article.title}
        Article Content: {article.content[:1000]}
        
        Respond with only 'yes' if the article is related to the topic, or 'no' if it's not.
        """
    
    @retry(
        stop=stop_after_attempt(settings.max_retries),
        wait=wait_exponential(multiplier=settings.retry_delay),
        reraise=True
    )
    async def _is_article_relevant(self, article: ArticleCreate, topic: str) -> bool:
        """
        Check if an article is relevant to the topic.
        
        Args:
            article: Article to check
            topic: Topic to check against
            
        Returns:
            bool: True if article is relevant, False otherwise
            
        Raises:
            ArticleFilterError: If OpenAI API call fails
        """
        try:
            response = await self.openai_client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise article classifier that responds only with 'yes' or 'no'."
                    },
                    {
                        "role": "user",
                        "content": self._create_filter_prompt(article, topic)
                    }
                ],
                temperature=settings.temperature,
                max_tokens=settings.max_tokens
            )
            answer = response.choices[0].message.content.strip().lower()
            return answer == "yes"
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise ArticleFilterError("Failed to check article relevance") from e
    
    async def filter(
        self,
        articles: List[ArticleCreate],
        topic: str
    ) -> List[ArticleCreate]:
        """
        Filter articles based on topic.
        
        Args:
            articles: List of articles to filter
            topic: Topic to filter by
            
        Returns:
            List of relevant articles
            
        Raises:
            ArticleFilterError: If filtering fails
        """
        try:
            relevant_articles = []
            
            for article in articles:
                try:
                    if await self._is_article_relevant(article, topic):
                        article.topic = topic
                        relevant_articles.append(article)
                except ArticleFilterError as e:
                    logger.warning(f"Failed to filter article '{article.title}': {e}")
                    continue
            
            logger.info(
                f"Filtered {len(relevant_articles)} relevant articles out of {len(articles)}"
            )
            return relevant_articles
            
        except Exception as e:
            logger.error(f"Article filtering failed: {e}")
            raise ArticleFilterError("Failed to filter articles") from e
