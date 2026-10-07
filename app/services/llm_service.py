import os
from typing import List, Optional
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from app.schemas.quiz import QuizOutput, ValidationResult
from app.prompts.quiz_prompt import quiz_prompt_template
from app.prompts.validation_prompt import validation_prompt_template


class LLMService:
    """Service class encapsulating LLM client interactions, prompt templates, and structured outputs."""

    FALLBACK_MODELS = [
        "gemini-3.1-flash-lite",
        "gemini-3.5-flash-lite",
        "gemini-3-flash-preview",
        "gemini-3.6-flash",
        "gemini-3.7-flash",
        "gemini-flash-latest"
    ]

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-3.1-flash-lite",
        temperature: float = 0.7
    ):
        load_dotenv()
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY must be set in the environment or passed to LLMService.")

        self.model_name = model or "gemini-3.1-flash-lite"
        self.temperature = temperature
        self._init_chains(self.model_name)

    def _init_chains(self, model_name: str):
        """Initializes the LangChain model and structured output chains for the given model name."""
        self.model_name = model_name
        self.llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=self.api_key,
            temperature=self.temperature
        )
        self.structured_quiz_generator = quiz_prompt_template | self.llm.with_structured_output(QuizOutput, method="json_schema")
        self.structured_validator = validation_prompt_template | self.llm.with_structured_output(ValidationResult, method="json_schema")

    def invoke(self, prompt: str) -> str:
        """Sends a text prompt to the LLM and returns the string response with fallback support."""
        models_to_try = [self.model_name] + [m for m in self.FALLBACK_MODELS if m != self.model_name]
        last_error = None

        for m in models_to_try:
            try:
                if m != self.model_name:
                    self._init_chains(m)
                response = self.llm.invoke(prompt)
                if isinstance(response.content, str):
                    return response.content
                elif isinstance(response.content, list):
                    text_parts = [
                        part.get("text", "") if isinstance(part, dict) else str(part)
                        for part in response.content
                    ]
                    return "".join(text_parts)
                return str(response.content)
            except Exception as e:
                last_error = e
                continue

        raise RuntimeError(f"All LLM candidate models failed: {last_error}")

    def generate_quiz(
        self,
        context: List[str],
        sport: str,
        difficulty: str = "Medium",
        critique: Optional[List[str]] = None
    ) -> QuizOutput:
        """
        Generates a 4-question multiple-choice quiz adhering to the QuizOutput Pydantic schema.
        Accepts optional validation critique for self-correction.
        """
        formatted_context = "\n".join(f"- {c}" for c in context) if context else "General sports knowledge."
        formatted_critique = "\n".join(f"- {c}" for c in critique) if critique else "None. This is the initial attempt."

        models_to_try = [self.model_name] + [m for m in self.FALLBACK_MODELS if m != self.model_name]
        last_error = None

        for m in models_to_try:
            try:
                if m != self.model_name:
                    self._init_chains(m)

                result = self.structured_quiz_generator.invoke({
                    "sport": sport,
                    "difficulty": difficulty,
                    "context": formatted_context,
                    "critique": formatted_critique
                })

                if isinstance(result, dict):
                    return QuizOutput.model_validate(result)
                return result
            except Exception as e:
                last_error = e
                continue

        raise RuntimeError(f"All LLM models failed to generate structured quiz: {last_error}")

    def validate_quiz(
        self,
        context: List[str],
        quiz: QuizOutput
    ) -> ValidationResult:
        """
        Evaluates a generated quiz against context, returning a structured ValidationResult.
        """
        formatted_context = "\n".join(f"- {c}" for c in context) if context else "General sports knowledge."
        quiz_json = quiz.model_dump_json(indent=2)

        models_to_try = [self.model_name] + [m for m in self.FALLBACK_MODELS if m != self.model_name]
        last_error = None

        for m in models_to_try:
            try:
                if m != self.model_name:
                    self._init_chains(m)

                result = self.structured_validator.invoke({
                    "context": formatted_context,
                    "quiz_data": quiz_json
                })

                if isinstance(result, dict):
                    return ValidationResult.model_validate(result)
                return result
            except Exception as e:
                last_error = e
                continue

        raise RuntimeError(f"All LLM models failed to validate quiz: {last_error}")
