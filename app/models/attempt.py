import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Float, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.quiz import Quiz


class QuizAttempt(Base):
    """SQLAlchemy ORM model representing a user's quiz attempt and score."""

    __tablename__ = "quiz_attempts"

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
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    percentage: Mapped[float] = mapped_column(Float, nullable=False)
    user_answers: Mapped[dict] = mapped_column(JSON, nullable=False)
    completed_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationship back to Quiz
    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="attempts")
