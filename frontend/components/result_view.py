from typing import Dict, Any, Callable, Optional
import streamlit as st
from frontend.components.context_view import render_research_context


def render_result_view(
    result_data: Dict[str, Any],
    on_reset: Callable[[], None],
    research_context: Optional[Dict[str, Any]] = None
):
    """Renders the evaluated quiz attempt scorecard, itemized breakdown, and source context."""
    score = result_data.get("score", 0)
    total = result_data.get("total_questions", 4)
    percentage = result_data.get("percentage", 0.0)
    attempt_id = result_data.get("attempt_id", "")
    quiz_id = result_data.get("quiz_id", "")
    results = result_data.get("results", [])

    st.success("🎉 Attempt Submitted & Recorded in Database!")

    # Summary Metrics Card
    col1, col2, col3 = st.columns(3)
    col1.metric("🏆 Final Score", f"{score} / {total}")
    col2.metric("📊 Accuracy", f"{percentage:.1f}%")
    col3.metric("📝 Attempt ID", f"`{attempt_id}`")

    st.caption(f"**Quiz Reference ID:** `{quiz_id}` (persisted in SQLite)")
    st.divider()

    st.subheader("📋 Itemized Review & Explanations")

    for item in results:
        q_idx = item.get("question_index", 1)
        question = item.get("question", "")
        selected = item.get("selected_option", "")
        correct = item.get("correct_answer", "")
        is_correct = item.get("is_correct", False)
        explanation = item.get("explanation", "")

        if is_correct:
            st.markdown(f"#### ✅ Question {q_idx}: Correct (+1)")
        else:
            st.markdown(f"#### ❌ Question {q_idx}: Incorrect (0)")

        st.write(f"**{question}**")
        st.write(f"- **Your Choice:** `{selected}`")
        if not is_correct:
            st.write(f"- **Correct Answer:** `{correct}`")

        with st.expander("💡 AI Fact Explanation"):
            st.write(explanation)

        st.divider()

    # Render RAG & Search context
    if research_context:
        render_research_context(research_context)
        st.divider()

    if st.button("🔄 Generate Another Quiz", use_container_width=True, type="secondary"):
        on_reset()
