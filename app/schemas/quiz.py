from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator


class QuestionItem(BaseModel):
    """Represents a single multiple-choice question with exactly 4 options (A, B, C, D)."""

    question: str = Field(
        ...,
        min_length=1,
        description="The question text testing factual sports knowledge."
    )
    options: Dict[str, str] = Field(
        ...,
        description="Dictionary mapping exactly keys 'A', 'B', 'C', and 'D' to option texts."
    )
    answer: Literal["A", "B", "C", "D"] = Field(
        ...,
        description="The key of the correct option ('A', 'B', 'C', or 'D')."
    )
    explanation: str = Field(
        ...,
        min_length=1,
        description="Detailed explanation justifying why the answer is correct based on context."
    )

    @field_validator("options")
    @classmethod
    def validate_options_keys(cls, v: Dict[str, str]) -> Dict[str, str]:
        required_keys = {"A", "B", "C", "D"}
        if set(v.keys()) != required_keys:
            raise ValueError(
                f"Options must contain exactly keys {sorted(required_keys)}, but got {sorted(v.keys())}"
            )
        for key in required_keys:
            if not v[key] or not str(v[key]).strip():
                raise ValueError(f"Option '{key}' cannot be empty.")
        return v


class QuizOutput(BaseModel):
    """Represents the complete generated quiz containing exactly 4 multiple-choice questions."""

    questions: List[QuestionItem] = Field(
        ...,
        min_length=4,
        max_length=4,
        description="List of exactly 4 structured multiple-choice questions."
    )


class ValidationResult(BaseModel):
    """Represents the evaluation verdict from the Quiz Validator Agent."""

    is_valid: bool = Field(
        ...,
        description="Whether the quiz passed all grounding, uniqueness, and formatting checks."
    )
    critique: List[str] = Field(
        default_factory=list,
        description="List of specific issues or feedback notes if validation failed."
    )
    score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Normalized quality score between 0.0 and 1.0."
    )


class NewsItem(BaseModel):
    """Represents a recent news item retrieved from web search."""
    title: str = Field(default="", description="News article title.")
    body: str = Field(default="", description="News article summary.")
    href: Optional[str] = Field(default=None, description="URL source link if available.")


class ResearchContext(BaseModel):
    """Encapsulates safe, user-facing retrieved historical facts and web news."""
    historical_facts: List[str] = Field(
        default_factory=list,
        description="Historical facts retrieved from ChromaDB vector store."
    )
    latest_news: List[NewsItem] = Field(
        default_factory=list,
        description="Recent news items retrieved via web search."
    )


class QuizGenerateRequest(BaseModel):
    """Request payload for quiz generation endpoint."""

    sport: str = Field(..., min_length=1, description="Target sport (e.g. Cricket, Football, Tennis).")
    difficulty: str = Field(default="Medium", description="Quiz difficulty: Easy, Medium, or Hard.")
    topic: Optional[str] = Field(default=None, description="Optional specific focus topic or tournament.")


class QuizGenerateResponse(BaseModel):
    """Response returned when a quiz is successfully generated and verified."""

    quiz_id: str = Field(..., description="Unique identifier for the generated quiz.")
    sport: str = Field(..., description="The sport topic of the quiz.")
    difficulty: str = Field(..., description="The difficulty level.")
    topic: Optional[str] = Field(default=None, description="The custom topic if specified.")
    questions: List[QuestionItem] = Field(..., description="List of 4 verified multiple-choice questions.")
    validation_score: float = Field(..., description="Quality verification score (0.0 to 1.0).")
    research_context: Optional[ResearchContext] = Field(
        default=None,
        description="Safe retrieved RAG facts and latest news context."
    )
