import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.attempt import QuizAttempt


class Quiz(Base):
    """SQLAlchemy ORM model representing a verified generated sports quiz."""

    __tablename__ = "quizzes"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())[:8]
    )
    sport: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    topic: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    difficulty: Mapped[str] = mapped_column(String(50), nullable=False)
    validation_score: Mapped[float] = mapped_column(Float, default=1.0)
    research_context: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships
    questions: Mapped[List["Question"]] = relationship(
        "Question",
        back_populates="quiz",
        cascade="all, delete-orphan",
        lazy="joined"
    )
    attempts: Mapped[List["QuizAttempt"]] = relationship(
        "QuizAttempt",
        back_populates="quiz",
        cascade="all, delete-orphan"
    )


class Question(Base):
    """SQLAlchemy ORM model representing a structured multiple-choice question."""

    __tablename__ = "questions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())[:8]
    )
    quiz_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("quizzes.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[dict] = mapped_column(JSON, nullable=False)
    correct_answer: Mapped[str] = mapped_column(String(5), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationship back to Quiz
    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="questions")
