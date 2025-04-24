from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import HttpUrl

class ArticleBase(SQLModel):
    """Base model for article data."""
    title: str = Field(index=True)
    url: str = Field(unique=True)  # Use str for SQLModel compatibility
    publication_date: datetime = Field(index=True)
    source: str = Field(index=True)
    content: str
    topic: Optional[str] = Field(default=None, index=True)

class Article(ArticleBase, table=True):
    """Database model for articles."""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ArticleCreate(ArticleBase):
    """Schema for creating new articles."""
    url: HttpUrl  # Use HttpUrl for Pydantic validation

class ArticleRead(ArticleBase):
    """Schema for reading articles."""
    id: int
    created_at: datetime
    updated_at: datetime

class ArticleUpdate(SQLModel):
    """Schema for updating articles."""
    title: Optional[str] = None
    content: Optional[str] = None
    topic: Optional[str] = None
