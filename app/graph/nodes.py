from typing import Dict, Any, Optional
from app.graph.state import AgentState
from app.services.rag_service import RAGService
from app.services.search_service import SearchService
from app.services.llm_service import LLMService
from app.schemas.quiz import QuizOutput, QuestionItem, ValidationResult


class QuizGraphNodes:
    """Encapsulates node execution logic for the quiz generation LangGraph."""

    def __init__(
        self,
        rag_service: Optional[RAGService] = None,
        search_service: Optional[SearchService] = None,
        llm_service: Optional[LLMService] = None,
    ):
        self.rag_service = rag_service or RAGService()
        self.search_service = search_service or SearchService()
        self.llm_service = llm_service or LLMService()

    def research_node(self, state: AgentState) -> Dict[str, Any]:
        """Gathers context from both ChromaDB vector store and DuckDuckGo search."""
        sport = state.get("sport", "Cricket")
        difficulty = state.get("difficulty", "Medium")
        topic = state.get("topic")

        query = topic if topic else f"{difficulty} {sport} rules and records"

        # 1. Retrieve historical facts from ChromaDB
        historical_facts = self.rag_service.retrieve_facts(
            sport=sport,
            query=query,
            n_results=2
        )

        # 2. Retrieve recent sports news
        news_items = self.search_service.search_recent_news(
            sport=sport,
            max_results=2
        )
        news_text_list = [
            f"Recent News: {item.get('title', '')} - {item.get('body', '')[:200]}"
            for item in news_items
        ]

        combined_context = historical_facts + news_text_list
        return {
            "context": combined_context,
            "status": "researching"
        }

    def generate_node(self, state: AgentState) -> Dict[str, Any]:
        """Generates 4 multiple-choice questions adhering to QuizOutput schema."""
        sport = state.get("sport", "Cricket")
        difficulty = state.get("difficulty", "Medium")
        context = state.get("context", [])
        validation = state.get("validation") or {}
        critique = validation.get("critique") if not validation.get("is_valid", True) else None

        quiz_output: QuizOutput = self.llm_service.generate_quiz(
            context=context,
            sport=sport,
            difficulty=difficulty,
            critique=critique
        )

        questions_data = [q.model_dump() for q in quiz_output.questions]
        return {
            "questions": questions_data,
            "status": "generating"
        }

    def validate_node(self, state: AgentState) -> Dict[str, Any]:
        """Evaluates generated quiz questions against context for accuracy and format."""
        context = state.get("context", [])
        questions_data = state.get("questions", [])

        # Reconstruct QuizOutput from serialized dicts
        question_items = [QuestionItem.model_validate(q) for q in questions_data]
        quiz_output = QuizOutput(questions=question_items)

        val_result: ValidationResult = self.llm_service.validate_quiz(
            context=context,
            quiz=quiz_output
        )

        current_retries = state.get("retry_count", 0)
        # Predictably increment retry_count on validation failure in a single place
        new_retry_count = current_retries + 1 if not val_result.is_valid else current_retries

        return {
            "validation": val_result.model_dump(),
            "retry_count": new_retry_count,
            "status": "validating"
        }

    def save_node(self, state: AgentState) -> Dict[str, Any]:
        """Marks successful completion of verified quiz (DB persistence in Phase 7)."""
        return {
            "status": "success",
            "error": None
        }

    def error_node(self, state: AgentState) -> Dict[str, Any]:
        """Handles final failure when validation retries are exhausted."""
        return {
            "status": "failed",
            "error": "Unable to generate a sufficiently validated quiz after 3 attempts."
        }


# Default singleton instance for top-level graph assembly
default_nodes = QuizGraphNodes()

def research_node(state: AgentState) -> Dict[str, Any]:
    return default_nodes.research_node(state)

def generate_node(state: AgentState) -> Dict[str, Any]:
    return default_nodes.generate_node(state)

def validate_node(state: AgentState) -> Dict[str, Any]:
    return default_nodes.validate_node(state)

def save_node(state: AgentState) -> Dict[str, Any]:
    return default_nodes.save_node(state)

def error_node(state: AgentState) -> Dict[str, Any]:
    return default_nodes.error_node(state)
