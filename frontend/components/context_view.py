from typing import Dict, Any, Optional
import streamlit as st


def render_research_context(research_context: Optional[Dict[str, Any]]):
    """Renders the AI Research Context (historical facts + latest web news) in clean expandable sections."""
    if not research_context:
        return

    hist_facts = research_context.get("historical_facts", [])
    latest_news = research_context.get("latest_news", [])

    if not hist_facts and not latest_news:
        return

    st.subheader("🔍 AI Context Used (RAG & Web Search)")

    if hist_facts:
        with st.expander("📚 Historical Sports Facts (ChromaDB Vector Store)"):
            for fact in hist_facts:
                st.markdown(f"- {fact}")

    if latest_news:
        with st.expander("📰 Latest Sports News (DuckDuckGo Search)"):
            for news in latest_news:
                title = news.get("title", "Recent Sports News")
                body = news.get("body", "")
                href = news.get("href")
                st.markdown(f"**{title}**")
                if body:
                    st.write(body)
                if href:
                    st.caption(f"[Source Link]({href})")
                st.divider()
