from src.generator import generate_quiz
 
if __name__ == "__main__":
    quiz = generate_quiz(
        sport="Cricket",
        difficulty="Hard"
    )
    print(quiz)