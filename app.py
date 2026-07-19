import streamlit as st
from src.generator import generate_quiz

# ---------------------------------------------------
# Page Configuration
# ---------------------------------------------------

st.set_page_config(
    page_title="AI Sports Quiz Generator",
    page_icon="🏆",
    layout="wide"
)

# ---------------------------------------------------
# Initialize Session State
# ---------------------------------------------------

if "result" not in st.session_state:
    st.session_state.result = None

if "score" not in st.session_state:
    st.session_state.score = 0

if "answered" not in st.session_state:
    st.session_state.answered = {}

# ---------------------------------------------------
# Title
# ---------------------------------------------------

st.title("🏆 AI Sports Quiz Generator")

st.markdown("""
Generate AI-powered sports quizzes using:

- 📚 Historical Sports Facts (ChromaDB)
- 📰 Latest Sports News (DuckDuckGo)
- 🤖 Gemini AI
""")

# ---------------------------------------------------
# Sidebar
# ---------------------------------------------------

with st.sidebar:

    st.header("⚙ Quiz Settings")

    sport = st.selectbox(
        "Select Sport",
        [
            "Cricket",
            "Football",
            "Basketball",
            "Tennis",
            "Hockey"
        ]
    )

    difficulty = st.selectbox(
        "Difficulty",
        [
            "Easy",
            "Medium",
            "Hard"
        ]
    )

    st.divider()

    if st.button("🚀 Generate Quiz", use_container_width=True):

        st.session_state.score = 0
        st.session_state.answered = {}

        with st.spinner("🤖 Generating AI Quiz..."):

            st.session_state.result = generate_quiz(
                sport=sport,
                difficulty=difficulty
            )

# ---------------------------------------------------
# Display Quiz
# ---------------------------------------------------

if st.session_state.result:

    result = st.session_state.result

    st.success("✅ Quiz generated successfully!")

    st.subheader(f"🏅 {sport} Quiz")

    st.write(f"**Difficulty:** {difficulty}")

    st.divider()

    questions = result["quiz"]["questions"]

    for i, q in enumerate(questions):

        st.markdown(f"## Question {i+1}")

        st.write(q["question"])

        options = list(q["options"].keys())

        selected = st.radio(
            "Choose your answer",
            options,
            format_func=lambda x: f"{x}. {q['options'][x]}",
            key=f"radio_{i}"
        )

        if st.button("Check Answer", key=f"button_{i}"):

            if i not in st.session_state.answered:

                st.session_state.answered[i] = True

                if selected == q["answer"]:
                    st.session_state.score += 1
                    st.success("✅ Correct!")
                else:
                    st.error("❌ Incorrect!")

                st.info(
                    f"Correct Answer: {q['answer']} - {q['options'][q['answer']]}"
                )

                st.write("**Explanation:**")

                st.write(q["explanation"])

        st.divider()

    # ---------------------------------------------------
    # Final Score
    # ---------------------------------------------------

    st.metric(
        "🏆 Current Score",
        f"{st.session_state.score} / {len(questions)}"
    )

    st.divider()

    # ---------------------------------------------------
    # RAG Context
    # ---------------------------------------------------

    st.subheader("🔍 AI Context Used")

    with st.expander("📚 Historical Facts"):

        for fact in result["historical_facts"]:
            st.markdown(f"- {fact}")

    with st.expander("📰 Latest News"):

        for news in result["latest_news"]:

            st.markdown(f"**{news['title']}**")

            st.write(news["body"])

            st.caption(news["href"])

            st.divider()

# ---------------------------------------------------
# Footer
# ---------------------------------------------------

st.divider()

st.caption(
    "Built with ❤️ using Streamlit • ChromaDB • DuckDuckGo • Gemini"
)