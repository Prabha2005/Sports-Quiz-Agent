import os
from typing import Generator
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.database.base import Base

load_dotenv()

# Default to local SQLite database with thread-check disabled for async/FastAPI compatibility
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sports_quiz.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initializes the database schema by creating all registered tables."""
    # Import models to ensure they are registered with Base.metadata
    from app.models.quiz import Quiz, Question  # noqa: F401
    from app.models.attempt import QuizAttempt  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
