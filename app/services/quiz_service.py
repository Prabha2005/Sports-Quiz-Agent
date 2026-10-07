import uuid
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.quiz import Quiz, Question
from app.models.attempt import QuizAttempt
from app.schemas.attempt import QuestionResultItem


class QuizService:
    """Service class encapsulating SQLAlchemy CRUD and scoring operations for Quizzes and Attempts."""

    def __init__(self, db: Session):
        self.db = db

    def create_quiz(
        self,
        sport: str,
        difficulty: str,
        topic: Optional[str],
        questions_data: List[Dict[str, Any]],
        validation_score: float = 1.0
    ) -> Quiz:
        """Creates and commits a new Quiz with its child Question records."""
        quiz_id = str(uuid.uuid4())[:8]

        quiz = Quiz(
            id=quiz_id,
            sport=sport,
            difficulty=difficulty,
            topic=topic,
            validation_score=validation_score
        )

        for q in questions_data:
            question_obj = Question(
                id=str(uuid.uuid4())[:8],
                quiz_id=quiz_id,
                question_text=q.get("question", ""),
                options=q.get("options", {}),
                correct_answer=q.get("answer", "").upper(),
                explanation=q.get("explanation", "")
            )
            quiz.questions.append(question_obj)

        self.db.add(quiz)
        self.db.commit()
        self.db.refresh(quiz)
        return quiz

    def get_quiz(self, quiz_id: str) -> Optional[Quiz]:
        """Fetches a Quiz by its ID along with its questions."""
        return self.db.query(Quiz).filter(Quiz.id == quiz_id).first()

    def submit_attempt(
        self,
        quiz_id: str,
        answers: Dict[str, str]
    ) -> Optional[Tuple[QuizAttempt, List[QuestionResultItem]]]:
        """
        Evaluates user answers against stored quiz answer keys,
        creates a QuizAttempt record, commits it, and returns the attempt & breakdown.
        """
        quiz = self.get_quiz(quiz_id)
        if not quiz:
            return None

        total_questions = len(quiz.questions)
        correct_count = 0
        results: List[QuestionResultItem] = []

        for idx, q in enumerate(quiz.questions, 1):
            # Match submitted answers by "1" or "0" based index string
            selected_option = (
                answers.get(str(idx))
                or answers.get(str(idx - 1))
                or ""
            ).upper()

            correct_answer = q.correct_answer.upper()
            is_correct = (selected_option == correct_answer)

            if is_correct:
                correct_count += 1

            results.append(
                QuestionResultItem(
                    question_index=idx,
                    question=q.question_text,
                    selected_option=selected_option or "None",
                    correct_answer=correct_answer,
                    is_correct=is_correct,
                    explanation=q.explanation
                )
            )

        percentage = round((correct_count / total_questions * 100.0), 2) if total_questions > 0 else 0.0

        attempt = QuizAttempt(
            id=str(uuid.uuid4())[:8],
            quiz_id=quiz_id,
            total_questions=total_questions,
            score=correct_count,
            percentage=percentage,
            user_answers=answers
        )

        self.db.add(attempt)
        self.db.commit()
        self.db.refresh(attempt)

        return attempt, results

    def get_attempt(self, attempt_id: str) -> Optional[QuizAttempt]:
        """Fetches a QuizAttempt by its ID."""
        return self.db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
