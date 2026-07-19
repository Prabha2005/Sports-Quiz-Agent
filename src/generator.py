from google import genai
from src.database import query_historic_facts
from src.search import search_latest_news
from src.config import client
import json

def build_prompt(sport, difficulty, historical_facts, latest_news):

    historical_text = "\n".join(
        f"- {fact}" for fact in historical_facts
    )

    latest_text = "\n".join(
    f"Title: {item['title']}\nSummary: {item['body'][:250]}"
    for item in latest_news
)
    
    prompt = f"""
You are an expert Sports Quiz Generator.

Use ONLY the information below.

SPORT:
{sport}

DIFFICULTY:
{difficulty}

Historical Facts:
{historical_text}

Latest News:
{latest_text}

Rules:

- Generate EXACTLY 4 multiple-choice questions.
- Test sports knowledge, not reading comprehension.
- Generate questions ONLY about the selected sport.
- Never ask questions about websites, article titles, news sources, or publication names.
- Never use phrases like:
  - "According to BBC"
  - "According to ESPN"
  - "According to Reuters"
  - "According to Cricbuzz"
- Focus on:
  - Players
  - Teams
  - Match results
  - Tournament winners
  - Rules
  - Records
  - Sporting achievements
- Mix historical facts with recent sports events whenever possible.
- Use ONLY the provided historical facts and latest news.
- Never invent facts.
- If the context is insufficient, use only the available facts instead of fabricating information.
- Each question must test a different concept.
- Ensure exactly one correct answer.
- Make incorrect options realistic but clearly incorrect.

Return ONLY valid JSON in the following format:

{{
  "questions": [
    {{
      "question": "...",
      "options": {{
        "A": "...",
        "B": "...",
        "C": "...",
        "D": "..."
      }},
      "answer": "A",
      "explanation": "..."
    }}
  ]
}}

Do not include markdown.
Do not wrap the response inside ```json.
Return JSON only.
"""




    return prompt


def generate_quiz(sport, difficulty="Medium"):

    historical_facts = query_historic_facts(
    sport=sport,
    query_text=f"{difficulty} {sport} quiz"
)

    latest_news = search_latest_news(sport)

    prompt = build_prompt(
        sport,
        difficulty,
        historical_facts,
        latest_news
    )

    response = client.models.generate_content(
    model="gemini-flash-latest",
    contents=prompt
)
    try:
        quiz = json.loads(response.text)
    
    except json.JSONDecodeError:
        raise ValueError(
        f"Gemini returned invalid JSON:\n\n{response.text}"
    )
    
    return {
    "quiz": quiz,
    "historical_facts": historical_facts,
    "latest_news": latest_news
}