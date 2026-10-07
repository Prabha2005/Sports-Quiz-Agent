from src.generator import generate_quiz

quiz = generate_quiz(
    sport="Cricket",
    difficulty="Hard"
)

print(quiz)