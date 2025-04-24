from datetime import datetime
from pathlib import Path
from typing import List, Optional
from loguru import logger
from sqlmodel import select

from src.collectors.collector import ArticleCollector
from src.filters.article_filter import ArticleFilter
from src.generators.pdf_generator import PDFGenerator
from src.models.article import Article, ArticleCreate
from src.models.database import get_session
from src.utils.exceptions import (
    ArticleCollectionError,
    ArticleFilterError,
    DatabaseError,
    PDFGenerationError
)

class NewsService:
    """Main service orchestrating the news automation workflow."""
    
    def __init__(self):
        """Initialize components."""
        self.collector = ArticleCollector()
        self.filter = ArticleFilter()
        self.pdf_generator = PDFGenerator()
    
    async def collect_and_filter_articles(
        self,
        source: str,
        topic: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Article]:
        """
        Collect and filter articles.
        
        Args:
            source: News source domain
            topic: Topic to filter by
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            List of filtered articles
            
        Raises:
            ArticleCollectionError: If collection fails
            ArticleFilterError: If filtering fails
            DatabaseError: If database operations fail
        """
        try:
            # Collect articles
            articles = await self.collector.get(
                source=source,
                start_date=start_date,
                end_date=end_date
            )
            
            # Filter articles
            filtered_articles = await self.filter.filter(articles, topic)
            
            # Save to database
            saved_articles = []
            with get_session() as session:
                for article in filtered_articles:
                    try:
                        article_dict = article.model_dump()
                        article_dict["url"] = str(article_dict["url"])
                        db_article = Article.model_validate(article_dict)
                        # Check if article with same URL already exists
                        existing_article = session.exec(select(Article).where(Article.url == db_article.url)).first()
                        if existing_article is None:
                            session.add(db_article)
                            session.commit()
                            session.refresh(db_article)
                            saved_articles.append(db_article)
                        else:
                            saved_articles.append(existing_article)
                            logger.info(f"Article with URL {db_article.url} already exists. Skipping insert.")
                    except Exception as e:
                        logger.warning(f"Failed to save article: {e}")
                        session.rollback()
            return saved_articles
            
        except Exception as e:
            logger.error(f"Failed to collect and filter articles: {e}")
            raise
    
    def get_saved_articles(
        self,
        topic: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Article]:
        """
        Get saved articles from database.
        
        Args:
            topic: Optional topic filter
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            List of articles
            
        Raises:
            DatabaseError: If database query fails
        """
        try:
            with get_session() as session:
                query = select(Article)
                
                if topic:
                    query = query.where(Article.topic == topic)
                if start_date:
                    query = query.where(Article.publication_date >= start_date)
                if end_date:
                    query = query.where(Article.publication_date <= end_date)
                
                return session.exec(query).all()
                
        except Exception as e:
            logger.error(f"Failed to get articles from database: {e}")
            raise DatabaseError("Failed to query database") from e
    
    def generate_pdf_report(self, articles: List[Article], topic: str) -> Path:
        """
        Generate PDF report for articles.
        
        Args:
            articles: List of articles
            topic: Topic of the articles
            
        Returns:
            Path to generated PDF
            
        Raises:
            PDFGenerationError: If PDF generation fails
        """
        try:
            return self.pdf_generator.generate_articles_pdf(articles, topic)
        except Exception as e:
            logger.error(f"Failed to generate PDF report: {e}")
            raise PDFGenerationError("Failed to generate PDF report") from e
