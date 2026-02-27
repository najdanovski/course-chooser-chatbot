def calculate_quiz_score(answers: dict):
    score = {
        "fullstack": 0,
        "frontend": 0,
        "design": 0,
        "marketing": 0,
        "accounting": 0,
        "management": 0
    }
    for _, selected in answers.items():
        if selected in score:
            score[selected] += 1
    recommendation = max(score, key=score.get)

    return recommendation, score


