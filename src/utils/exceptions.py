class NewsAutomationError(Exception):
    """Base exception for news automation errors."""
    pass

class ArticleCollectionError(NewsAutomationError):
    """Raised when article collection fails."""
    pass

class ArticleFilterError(NewsAutomationError):
    """Raised when article filtering fails."""
    pass

class PDFGenerationError(NewsAutomationError):
    """Raised when PDF generation fails."""
    pass

class DatabaseError(NewsAutomationError):
    """Raised when database operations fail."""
    pass
