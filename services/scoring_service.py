def calculate_quiz_score(answers: dict):
    score = {
        "fullstack": 0,
        "frontend": 0,
        "design": 0,
        "marketing": 0,
        "accounting": 0,
        "management": 0
    }

    if answers["q1"] in score:
        score[answers["q1"]] += 3

    if answers["q2"] == "logic":
        score["fullstack"] += 4
        score["frontend"] += 3
        score["accounting"] += 2
    elif answers["q2"] == "visual":
        score["design"] += 4
        score["frontend"] += 3
    elif answers["q2"] == "analysis":
        score["accounting"] += 4
        score["management"] += 3
    elif answers["q2"] == "communication":
        score["marketing"] += 4
        score["management"] += 3

    if answers["q3"] == "solo":
        score["fullstack"] += 3
        score["frontend"] += 2
        score["accounting"] += 2
    elif answers["q3"] == "team":
        score["design"] += 3
        score["marketing"] += 2
        score["management"] += 2
    elif answers["q3"] == "mixed":
        score["management"] += 3

    if answers["q4"] == "technology":
        score["fullstack"] += 4
        score["frontend"] += 3
    elif answers["q4"] == "creativity":
        score["design"] += 4
        score["frontend"] += 3
    elif answers["q4"] == "stability":
        score["accounting"] += 4
        score["management"] += 3
    elif answers["q4"] == "business":
        score["marketing"] += 4
        score["management"] += 3

    if answers["q5"] == "very_high":
        score["fullstack"] += 2
        score["frontend"] += 2
        score["design"] += 2
        score["marketing"] += 2
        score["accounting"] += 2
        score["management"] += 2
    elif answers["q5"] == "high":
        score["fullstack"] += 2
        score["frontend"] += 2
        score["design"] += 2
        score["marketing"] += 2
        score["accounting"] += 2
        score["management"] += 2
    elif answers["q5"] == "medium":
        score["fullstack"] += 1
        score["frontend"] += 1
        score["design"] += 1
        score["marketing"] += 1
        score["accounting"] += 1
        score["management"] += 1
    elif answers["q5"] == "low":
        score["fullstack"] += 0
        score["frontend"] += 0
        score["design"] += 0
        score["marketing"] += 0
        score["accounting"] += 0
        score["management"] += 0

    recommended = max(score, key=score.get)
    for key in score:
        if score[key] > 15:
            score[key] = 15

    return recommended, score


