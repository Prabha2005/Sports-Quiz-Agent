from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.attempt import (
    SubmitAttemptRequest,
    AttemptResultResponse,
    QuestionResultItem,
)
from app.api.deps import get_quiz_service
from app.services.quiz_service import QuizService

router = APIRouter(prefix="/attempts", tags=["Attempts"])


@router.post(
    "/submit",
    response_model=AttemptResultResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit answers for a quiz, evaluate score, and persist attempt"
)
def submit_attempt_endpoint(
    request: SubmitAttemptRequest,
    quiz_service: QuizService = Depends(get_quiz_service)
):
    """
    Submits user answers for a quiz, evaluates correctness against database questions,
    persists the attempt in SQLite, and returns the score breakdown.
    """
    result = quiz_service.submit_attempt(
        quiz_id=request.quiz_id,
        answers=request.answers
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quiz with ID '{request.quiz_id}' was not found."
        )

    attempt, results = result

    return AttemptResultResponse(
        attempt_id=attempt.id,
        quiz_id=attempt.quiz_id,
        score=attempt.score,
        total_questions=attempt.total_questions,
        percentage=attempt.percentage,
        results=results
    )
