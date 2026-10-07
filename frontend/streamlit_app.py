import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from frontend.api_client import APIClient
from frontend.components.quiz_view import render_quiz_view
from frontend.components.result_view import render_result_view

# -------------------------------------------------------------
# Page Configuration
# -------------------------------------------------------------
st.set_page_config(
    page_title="Agentic AI Sports Quiz Platform",
    page_icon="🏆",
    layout="wide"
)

# Initialize API Client
api_client = APIClient()

# -------------------------------------------------------------
# Session State Initialization
# -------------------------------------------------------------
if "current_quiz" not in st.session_state:
    st.session_state.current_quiz = None

if "current_result" not in st.session_state:
    st.session_state.current_result = None

if "current_research_context" not in st.session_state:
    st.session_state.current_research_context = None

if "error_message" not in st.session_state:
    st.session_state.error_message = None


def reset_quiz_state():
    """Resets all frontend state for a fresh quiz generation."""
    st.session_state.current_quiz = None
    st.session_state.current_result = None
    st.session_state.current_research_context = None
    st.session_state.error_message = None
    st.session_state.selected_answers = {}


def handle_submit_attempt(answers: dict):
    """Submits user answers to the FastAPI backend."""
    if not st.session_state.current_quiz:
        return
    quiz_id = st.session_state.current_quiz.get("quiz_id")
    research_ctx = st.session_state.current_quiz.get("research_context")
    with st.spinner("📊 Evaluating answers and recording score in SQLite..."):
        res = api_client.submit_attempt(quiz_id=quiz_id, answers=answers)
        if res.get("success"):
            st.session_state.current_result = res["data"]
            st.session_state.current_research_context = research_ctx
            st.session_state.current_quiz = None
            st.rerun()
        else:
            st.error(f"❌ Failed to submit attempt: {res.get('error')}")


# -------------------------------------------------------------
# Sidebar Configuration
# -------------------------------------------------------------
with st.sidebar:
    st.header("⚙ Quiz Settings")

    # Backend Connection Status Check
    health = api_client.check_health()
    if health.get("connected"):
        st.success("🟢 FastAPI Backend Connected")
    else:
        st.warning("⚠️ FastAPI Disconnected (Run `uvicorn app.main:app`)")

    st.divider()

    sport = st.selectbox(
        "Select Sport",
        ["Cricket", "Football", "Basketball", "Tennis", "Hockey"]
    )

    difficulty = st.selectbox(
        "Select Difficulty",
        ["Easy", "Medium", "Hard"],
        index=1
    )

    topic = st.text_input(
        "Custom Topic / Event (Optional)",
        placeholder="e.g. 2024 T20 World Cup, UEFA Champions League"
    )

    st.divider()

    if st.button("🚀 Generate AI Quiz", use_container_width=True, type="primary"):
        reset_quiz_state()
        with st.spinner("🤖 Orchestrating Multi-Agent Workflow (Research ➔ Generate ➔ Validate)..."):
            res = api_client.generate_quiz(
                sport=sport,
                difficulty=difficulty,
                topic=topic
            )
            if res.get("success"):
                st.session_state.current_quiz = res["data"]
                st.rerun()
            else:
                st.session_state.error_message = res.get("error")

    st.divider()

    # Direct Quiz Lookup by ID
    st.subheader("🔍 Find Existing Quiz")
    lookup_id = st.text_input("Enter Quiz ID", placeholder="e.g. f0b7593f")
    if st.button("Load Quiz by ID", use_container_width=True):
        if lookup_id.strip():
            reset_quiz_state()
            with st.spinner("Fetching quiz from SQLite..."):
                res = api_client.get_quiz(lookup_id.strip())
                if res.get("success"):
                    st.session_state.current_quiz = res["data"]
                    st.rerun()
                else:
                    st.session_state.error_message = res.get("error")


# -------------------------------------------------------------
# Main Application Content
# -------------------------------------------------------------
st.title("🏆 Agentic AI Sports Research & Quiz Platform")
st.markdown("""
A modular, production-oriented stateful multi-agent sports quiz platform powered by:
- 🧠 **LangGraph Multi-Agent Engine** (Research, Generation, Fact-Checking, and Self-Correction)
- 📚 **RAG via ChromaDB** (Historical sports knowledge retrieval)
- 📰 **Live DuckDuckGo Search** (Up-to-date tournament and match data)
- ⚡ **FastAPI & Pydantic v2** (Typed async REST endpoints)
- 💾 **SQLite & SQLAlchemy 2.0** (Persistent relational storage for quizzes and scored attempts)
""")

st.divider()

# Display any error messages
if st.session_state.error_message:
    st.error(f"❌ {st.session_state.error_message}")
    if st.button("Dismiss"):
        st.session_state.error_message = None
        st.rerun()

# 1. Active Quiz View
if st.session_state.current_quiz:
    render_quiz_view(
        quiz_data=st.session_state.current_quiz,
        on_submit=handle_submit_attempt
    )

# 2. Result Scorecard View
elif st.session_state.current_result:
    render_result_view(
        result_data=st.session_state.current_result,
        on_reset=reset_quiz_state,
        research_context=st.session_state.current_research_context
    )

# 3. Idle Welcome View
else:
    st.info("👈 Use the sidebar to select your sport and difficulty, then click **'Generate AI Quiz'** to trigger the multi-agent graph.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### 🔄 Multi-Agent Workflow
        1. **Research Agent:** Queries ChromaDB for historical facts and fetches recent sports news.
        2. **Generator Agent:** Generates 4 strictly-formatted multiple choice questions.
        3. **Validator Agent:** Fact-checks options and answers against retrieved context.
        4. **Self-Correction Loop:** If validation rejects the quiz, cycles back with critique (up to 3 retries).
        5. **Persistence Node:** Saves verified quizzes and scores into SQLite via SQLAlchemy.
        """)

    with col2:
        st.markdown("""
        ### 📊 System Features
        - **Decoupled Architecture:** Frontend communicates exclusively through typed REST APIs.
        - **Data Integrity:** Invalid quizzes are rejected by the validator and never saved.
        - **Persistent Attempts:** Scores, answer keys, and explanations are preserved in SQLite.
        """)
