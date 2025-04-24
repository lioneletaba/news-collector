from contextlib import contextmanager
from typing import Generator
from sqlmodel import Session, SQLModel, create_engine
from loguru import logger
from src.utils.config import get_settings

settings = get_settings()

# Create database engine
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

def create_db_and_tables() -> None:
    """Create database and tables."""
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("Database and tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database and tables: {e}")
        raise

@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Get database session."""
    session = Session(engine)
    try:
        yield session
    except Exception as e:
        logger.error(f"Database session error: {e}")
        session.rollback()
        raise
    finally:
        session.close()
