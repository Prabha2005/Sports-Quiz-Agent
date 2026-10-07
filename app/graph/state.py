from typing import TypedDict, Optional, List, Dict, Any


class AgentState(TypedDict):
    """Minimally defined state schema for the LangGraph multi-agent workflow."""

    sport: str
    topic: Optional[str]
    difficulty: str
    context: List[str]
    questions: List[Dict[str, Any]]
    validation: Optional[Dict[str, Any]]
    retry_count: int
    status: str  # "pending", "success", "failed"
    error: Optional[str]
