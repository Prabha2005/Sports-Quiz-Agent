from typing import Dict, List
from pydantic import BaseModel, Field


class SubmitAttemptRequest(BaseModel):
    """Request payload when a user submits answers for a quiz."""

    quiz_id: str = Field(..., min_length=1, description="ID of the quiz being answered.")
    answers: Dict[str, str] = Field(
        ...,
        description="Dictionary mapping question index ('1', '2', '3', '4' or 1-based index) to selected option ('A', 'B', 'C', 'D')."
    )


class QuestionResultItem(BaseModel):
    """Detailed score breakdown for an individual question."""

    question_index: int = Field(..., description="1-based index of the question.")
    question: str = Field(..., description="Question text.")
    selected_option: str = Field(..., description="The option chosen by the user.")
    correct_answer: str = Field(..., description="The correct answer key.")
    is_correct: bool = Field(..., description="Whether the user selected the correct answer.")
    explanation: str = Field(..., description="Explanation of the correct answer.")


class AttemptResultResponse(BaseModel):
    """Result response summarizing quiz performance."""

    attempt_id: str = Field(..., description="Unique ID for this attempt.")
    quiz_id: str = Field(..., description="Associated quiz ID.")
    score: int = Field(..., description="Number of correctly answered questions.")
    total_questions: int = Field(..., description="Total number of questions.")
    percentage: float = Field(..., description="Score percentage (0.0 to 100.0).")
    results: List[QuestionResultItem] = Field(..., description="Itemized breakdown per question.")
