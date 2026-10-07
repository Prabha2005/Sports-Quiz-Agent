from typing import Dict, Any, Callable
import streamlit as st
from frontend.components.context_view import render_research_context


def render_quiz_view(quiz_data: Dict[str, Any], on_submit: Callable[[Dict[str, str]], None]):
    """Renders the active quiz interface with 4 multiple-choice questions."""
    sport = quiz_data.get("sport", "Sports")
    difficulty = quiz_data.get("difficulty", "Medium")
    topic = quiz_data.get("topic")
    quiz_id = quiz_data.get("quiz_id", "")
    val_score = quiz_data.get("validation_score", 1.0)
    questions = quiz_data.get("questions", [])
    research_context = quiz_data.get("research_context")

    st.subheader(f"🏅 {sport} Quiz ({difficulty})")
    if topic:
        st.caption(f"**Focus Topic:** {topic}")

    cols = st.columns([2, 1, 1])
    cols[0].caption(f"**Quiz ID:** `{quiz_id}`")
    cols[1].caption(f"**Total Questions:** {len(questions)}")
    cols[2].caption(f"**AI Quality Score:** {val_score:.2f}")

    st.divider()

    # Track answers in a dictionary keyed by "1", "2", "3", "4"
    if "selected_answers" not in st.session_state:
        st.session_state.selected_answers = {}

    for idx, q in enumerate(questions, 1):
        st.markdown(f"### Question {idx}")
        st.write(f"**{q.get('question', '')}**")

        options = q.get("options", {})
        option_keys = sorted(options.keys())

        # Current selection for this question
        current_choice = st.session_state.selected_answers.get(str(idx), "A")

        selected = st.radio(
            f"Select your answer for Question {idx}:",
            option_keys,
            index=option_keys.index(current_choice) if current_choice in option_keys else 0,
            format_func=lambda k: f"{k}. {options.get(k, '')}",
            key=f"q_radio_{quiz_id}_{idx}"
        )
        st.session_state.selected_answers[str(idx)] = selected
        st.divider()

    col_btn, _ = st.columns([1, 2])
    with col_btn:
        if st.button("🚀 Submit Quiz Attempt", use_container_width=True, type="primary"):
            on_submit(st.session_state.selected_answers)

    # Render RAG & Search context
    if research_context:
        st.divider()
        render_research_context(research_context)
