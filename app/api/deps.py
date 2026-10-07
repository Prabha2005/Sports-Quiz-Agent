from typing import Generator, Dict, Any, Optional, List
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.quiz_service import QuizService
from app.graph import quiz_graph


def get_quiz_service(db: Session = Depends(get_db)) -> QuizService:
    """Dependency provider for the SQLAlchemy QuizService."""
    return QuizService(db)


def get_quiz_graph():
    """Dependency provider for the compiled LangGraph workflow."""
    return quiz_graph


class InMemoryQuizStore:
    """In-memory store maintained for backward compatibility in mock tests."""

    def __init__(self):
        self._quizzes: Dict[str, Dict[str, Any]] = {}
        self._attempts: Dict[str, Dict[str, Any]] = {}

    def save_quiz(self, sport: str, difficulty: str, topic: Optional[str], questions: List[Dict[str, Any]], validation_score: float) -> str:
        import uuid
        quiz_id = str(uuid.uuid4())[:8]
        self._quizzes[quiz_id] = {
            "quiz_id": quiz_id,
            "sport": sport,
            "difficulty": difficulty,
            "topic": topic,
            "questions": questions,
            "validation_score": validation_score,
        }
        return quiz_id

    def get_quiz(self, quiz_id: str) -> Optional[Dict[str, Any]]:
        return self._quizzes.get(quiz_id)

    def save_attempt(self, attempt_data: Dict[str, Any]) -> str:
        import uuid
        attempt_id = str(uuid.uuid4())[:8]
        attempt_data["attempt_id"] = attempt_id
        self._attempts[attempt_id] = attempt_data
        return attempt_id

    def get_attempt(self, attempt_id: str) -> Optional[Dict[str, Any]]:
        return self._attempts.get(attempt_id)


_store_instance = InMemoryQuizStore()


def get_quiz_store() -> InMemoryQuizStore:
    return _store_instance
