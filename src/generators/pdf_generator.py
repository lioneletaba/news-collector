from datetime import datetime
from pathlib import Path
from typing import List
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from loguru import logger

from src.models.article import Article
from src.utils.config import get_settings
from src.utils.exceptions import PDFGenerationError

settings = get_settings()

class PDFGenerator:
    """Generate PDF reports from articles."""
    
    def __init__(self):
        """Initialize PDF styles."""
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles."""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        self.article_title_style = ParagraphStyle(
            'ArticleTitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=20,
            spaceAfter=10
        )
        
        self.metadata_style = ParagraphStyle(
            'Metadata',
            parent=self.styles['Italic'],
            fontSize=10,
            textColor=colors.gray
        )
    
    def _create_header(self, story: List, topic: str):
        """Add header to the PDF."""
        # Add title
        title = f"News Report: {topic}"
        story.append(Paragraph(title, self.title_style))
        
        # Add date
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        story.append(Paragraph(f"Generated on: {date_str}", self.metadata_style))
        story.append(Spacer(1, 20))
    
    def _add_article(self, story: List, article: Article):
        """Add an article to the PDF."""
        # Article title with URL
        title_with_link = f'<link href="{article.url}">{article.title}</link>'
        story.append(Paragraph(title_with_link, self.article_title_style))
        
        # Metadata
        metadata = (
            f"Source: {article.source} | "
            f"Published: {article.publication_date.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        story.append(Paragraph(metadata, self.metadata_style))
        story.append(Spacer(1, 10))
        
        # Content
        content = article.content[:1000] + "..." if len(article.content) > 1000 else article.content
        story.append(Paragraph(content, self.styles['Normal']))
        story.append(Spacer(1, 20))
    
    def generate_articles_pdf(self, articles: List[Article], topic: str) -> Path:
        """
        Generate PDF report from articles.
        
        Args:
            articles: List of articles to include
            topic: Topic of the articles
            
        Returns:
            Path to generated PDF file
            
        Raises:
            PDFGenerationError: If PDF generation fails
        """
        try:
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = settings.pdf_export_dir / f"news_report_{timestamp}.pdf"
            
            # Create PDF document
            doc = SimpleDocTemplate(
                str(filename),
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Create story (content)
            story = []
            
            # Add header
            self._create_header(story, topic)
            
            # Add articles
            for article in articles:
                self._add_article(story, article)
            
            # Build PDF
            doc.build(story)
            logger.info(f"Generated PDF report: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Failed to generate PDF: {e}")
            raise PDFGenerationError("Failed to generate PDF report") from e
