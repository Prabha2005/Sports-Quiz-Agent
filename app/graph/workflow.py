from langgraph.graph import StateGraph, START, END
from app.graph.state import AgentState
from app.graph.nodes import (
    QuizGraphNodes,
    research_node,
    generate_node,
    validate_node,
    save_node,
    error_node,
)


def route_after_validation(state: AgentState) -> str:
    """
    Conditional routing edge evaluating validation status:
    - If validation is valid -> route to 'save'
    - If validation failed and retry_count < 3 -> route to 'generate' for self-correction
    - If retry_count >= 3 -> route to 'error' (prevents saving invalid quiz)
    """
    validation = state.get("validation") or {}
    if validation.get("is_valid", False):
        return "save"

    if state.get("retry_count", 0) < 3:
        return "generate"

    return "error"


def create_quiz_graph(custom_nodes: QuizGraphNodes = None):
    """Factory function to construct and compile the LangGraph multi-agent workflow."""
    nodes = custom_nodes if custom_nodes else QuizGraphNodes()

    builder = StateGraph(AgentState)

    # 1. Add Workflow Nodes
    builder.add_node("research", nodes.research_node)
    builder.add_node("generate", nodes.generate_node)
    builder.add_node("validate", nodes.validate_node)
    builder.add_node("save", nodes.save_node)
    builder.add_node("error", nodes.error_node)

    # 2. Add Linear Edges
    builder.add_edge(START, "research")
    builder.add_edge("research", "generate")
    builder.add_edge("generate", "validate")

    # 3. Add Conditional Routing Edge from validate node
    builder.add_conditional_edges(
        "validate",
        route_after_validation,
        {
            "save": "save",
            "generate": "generate",
            "error": "error"
        }
    )

    # 4. Terminal Edges to END
    builder.add_edge("save", END)
    builder.add_edge("error", END)

    return builder.compile()


# Default compiled graph ready for execution
quiz_graph = create_quiz_graph()
