from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.quiz import (
    QuizGenerateRequest,
    QuizGenerateResponse,
    QuestionItem,
    ResearchContext,
    NewsItem,
)
from app.graph.state import AgentState
from app.api.deps import get_quiz_service, get_quiz_graph
from app.services.quiz_service import QuizService

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])


@router.post(
    "/generate",
    response_model=QuizGenerateResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate and persist a verified sports quiz via LangGraph"
)
def generate_quiz_endpoint(
    request: QuizGenerateRequest,
    graph=Depends(get_quiz_graph),
    quiz_service: QuizService = Depends(get_quiz_service)
):
    """
    Triggers the LangGraph multi-agent workflow (Research -> Generate -> Validate -> Conditional Retry).
    Upon verified success, commits the quiz and its questions to SQLite via SQLAlchemy.
    Returns 200 with the verified quiz, or 422 if validation criteria cannot be satisfied.
    """
    initial_state: AgentState = {
        "sport": request.sport,
        "topic": request.topic,
        "difficulty": request.difficulty,
        "context": [],
        "historical_facts": [],
        "latest_news": [],
        "questions": [],
        "validation": None,
        "retry_count": 0,
        "status": "pending",
        "error": None
    }

    try:
        final_state: AgentState = graph.invoke(initial_state)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Graph execution failed with unexpected error: {str(e)}"
        )

    # Check graph completion outcome
    if final_state.get("status") == "failed":
        error_msg = final_state.get("error") or "Unable to generate a sufficiently validated quiz after 3 attempts."
        raise HTTPException(
            status_code=getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", 422),
            detail=error_msg
        )

    questions_data = final_state.get("questions", [])
    validation_data = final_state.get("validation") or {}
    validation_score = float(validation_data.get("score", 1.0))

    # Convert to typed QuestionItem models
    typed_questions = [QuestionItem.model_validate(q) for q in questions_data]

    # Build safe research context
    raw_hist = final_state.get("historical_facts") or []
    raw_news = final_state.get("latest_news") or []
    typed_news = [
        NewsItem(
            title=item.get("title", ""),
            body=item.get("body", ""),
            href=item.get("href")
        )
        for item in raw_news
    ]
    research_ctx = ResearchContext(
        historical_facts=raw_hist,
        latest_news=typed_news
    )

    # Persist in SQLite via SQLAlchemy QuizService
    quiz_record = quiz_service.create_quiz(
        sport=request.sport,
        difficulty=request.difficulty,
        topic=request.topic,
        questions_data=[q.model_dump() for q in typed_questions],
        validation_score=validation_score,
        research_context=research_ctx.model_dump()
    )

    return QuizGenerateResponse(
        quiz_id=quiz_record.id,
        sport=quiz_record.sport,
        difficulty=quiz_record.difficulty,
        topic=quiz_record.topic,
        questions=typed_questions,
        validation_score=quiz_record.validation_score,
        research_context=research_ctx
    )


@router.get(
    "/{quiz_id}",
    response_model=QuizGenerateResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve a quiz by its ID from the database"
)
def get_quiz_endpoint(
    quiz_id: str,
    quiz_service: QuizService = Depends(get_quiz_service)
):
    """Retrieves an existing persisted quiz by its unique quiz_id from SQLite."""
    quiz_record = quiz_service.get_quiz(quiz_id)
    if not quiz_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quiz with ID '{quiz_id}' was not found."
        )

    typed_questions = [
        QuestionItem(
            question=q.question_text,
            options=q.options,
            answer=q.correct_answer,
            explanation=q.explanation
        )
        for q in quiz_record.questions
    ]

    research_ctx = None
    if quiz_record.research_context:
        try:
            research_ctx = ResearchContext.model_validate(quiz_record.research_context)
        except Exception:
            research_ctx = None

    return QuizGenerateResponse(
        quiz_id=quiz_record.id,
        sport=quiz_record.sport,
        difficulty=quiz_record.difficulty,
        topic=quiz_record.topic,
        questions=typed_questions,
        validation_score=quiz_record.validation_score,
        research_context=research_ctx
    )
