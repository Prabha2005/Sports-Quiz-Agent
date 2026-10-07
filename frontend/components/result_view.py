from typing import Dict, Any, Callable
import streamlit as st


def render_result_view(result_data: Dict[str, Any], on_reset: Callable[[], None]):
    """Renders the evaluated quiz attempt scorecard and itemized breakdown."""
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

    if st.button("🔄 Generate Another Quiz", use_container_width=True, type="secondary"):
        on_reset()
