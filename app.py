from flask import Flask, render_template, request, redirect, url_for, flash, session as flask_session
from datetime import datetime
import json
import os

from database import session
from models import QuizResult, AIAdvice
from services.scoring_service import calculate_quiz_score
from services.ai_service import generate_explanation

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

QUESTIONS = [
    {"id": "q1", "text": "Што те интересира најмногу?", "options": [("fullstack","Full Stack / Веб"),("frontend","Front-end"),("design","Дизајн"),("marketing","Маркетинг"),("accounting","Сметководство"),("management","Менаџмент")]},
    {"id": "q2", "text": "Колку ти се допаѓа математика и логика?", "options": [("logic","Многу – сакам решавачки задачи"),("visual","Повеќе визуелно / креативно"),("analysis","Аналитика и податоци"),("communication","Работа со луѓе")]},
    {"id": "q3", "text": "Како сакаш да работиш?", "options": [("solo","Самостојно"),("team","Во тим"),("mixed","Комбинирано")]},
    {"id": "q4", "text": "Кој тип задачи те привлекуваат?", "options": [("technology","Технологија / кодирање"),("creativity","Креативност"),("stability","Стабилност"),("business","Бизнис")]},
    {"id": "q5", "text": "Колку време неделно можеш да посветиш?", "options": [("very_high","5+ часа"),("high","3–5 часа"),("medium","1–3 часа"),("low","Под 1 час")]}
]

RECOMMENDATIONS = {
    'fullstack': ('Full Stack Developer', 'Комбинација од логика, кодирање и практична работа.'),
    'frontend': ('Front-End Developer', 'Фокус на интерфејс и корисничко искуство.'),
    'design': ('UX/UI & Graphic Design', 'Силен креативен и визуелен интерес.'),
    'marketing': ('Digital Marketing & SEO', 'Бизнис ориентиран и комуникативен профил.'),
    'accounting': ('Accounting', 'Точност, анализа и работа со бројки.'),
    'management': ('Management', 'Организациски и лидерски способности.')
}

def get_user_answers(r):
    return [
        {"question_text": "Интерес", "answer_text": r.q1_answer},
        {"question_text": "Логика / Математика", "answer_text": r.q2_answer},
        {"question_text": "Тим или самостојно", "answer_text": r.q3_answer},
        {"question_text": "Кариерна цел", "answer_text": r.q4_answer},
        {"question_text": "Време неделно", "answer_text": r.q5_answer},
    ]

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    step = int(request.args.get("step", 0))
    total = len(QUESTIONS)
    answers = flask_session.setdefault("quiz_answers", {})

    if request.method == "POST":
        answer = request.form.get("answer")
        if not answer:
            flash("Ве молиме одберете одговор.", "error")
            return redirect(url_for("quiz", step=step))
        answers[QUESTIONS[step]["id"]] = answer
        flask_session["quiz_answers"] = answers
        if step + 1 < total:
            return redirect(url_for("quiz", step=step + 1))

        recommendation, scores = calculate_quiz_score(answers)
        result = QuizResult(
            created_at=datetime.utcnow(),
            **{f"q{i+1}_answer": answers.get(f"q{i+1}") for i in range(total)},
            score=scores,
            recommendation=recommendation
        )
        session.add(result)
        session.commit()
        flask_session.pop("quiz_answers", None)
        return redirect(url_for("result_detail", result_id=result.id))

    if step < 0 or step >= total:
        return redirect(url_for("quiz", step=0))

    question = QUESTIONS[step]
    return render_template("quiz_form.html", question=question, step=step, total=total, saved_answer=answers.get(question["id"]))

@app.route("/results")
def results_list():
    rows = session.query(QuizResult).order_by(QuizResult.created_at.desc()).all()
    results = [{
        "id": r.id,
        "created_at": r.created_at,
        "recommended_course": RECOMMENDATIONS.get(r.recommendation, ("Unknown", ""))[0],
        "recommendation": r.recommendation,
        "recommendation_reason": RECOMMENDATIONS.get(r.recommendation, ("",""))[1],
        "score": r.score,
        "user_answers": get_user_answers(r),
        "ai_explanation": json.loads(r.ai_advice.content) if r.ai_advice else None
    } for r in rows]
    return render_template("results_list.html", results=results)

@app.route("/results/<int:result_id>")
def result_detail(result_id):
    r = session.get(QuizResult, result_id)
    if not r:
        flash("Резултатот не беше најден.", "error")
        return redirect(url_for("results_list"))
    result = {
        "id": r.id,
        "created_at": r.created_at,
        "recommended_course": RECOMMENDATIONS.get(r.recommendation, ("Unknown",""))[0],
        "recommendation": r.recommendation,
        "recommendation_reason": RECOMMENDATIONS.get(r.recommendation, ("",""))[1],
        "score": r.score,
        "user_answers": get_user_answers(r),
        "ai_explanation": json.loads(r.ai_advice.content) if r.ai_advice else None
    }
    return render_template("result_detail.html", result=result)

@app.route("/ai_explain/<int:result_id>", methods=["POST"])
def ai_explain(result_id):
    r = session.get(QuizResult, result_id)
    if not r:
        flash("Резултатот не беше најден.", "error")
        return redirect(url_for("results_list"))

    answers = {f"q{i+1}": getattr(r, f"q{i+1}_answer") for i in range(5)}
    ai_result = generate_explanation(answers, r.recommendation)

    if not ai_result:
        fallback = {
            "fullstack": {"title":"Full Stack Developer","explanation":"Комбинација од логика, кодирање и практична работа.","tips":["HTML/CSS","JavaScript","Flask/Django"]},
            "frontend": {"title":"Front-End Developer","explanation":"Фокус на интерфејс и корисничко искуство.","tips":["HTML/CSS","JavaScript","React"]},
            "design": {"title":"UX/UI & Graphic Design","explanation":"Силен креативен и визуелен интерес.","tips":["Figma","UX принципи","Портфолио"]},
            "marketing": {"title":"Digital Marketing","explanation":"Бизнис ориентиран и комуникативен профил.","tips":["SEO","Social Media","Analytics"]},
            "accounting": {"title":"Accounting","explanation":"Точност, анализа и работа со бројки.","tips":["Excel","Финансии","Основи на сметководство"]},
            "management": {"title":"Management","explanation":"Организациски и лидерски способности.","tips":["Project Management","Soft skills","Бизнис стратегии"]}
        }
        content_obj = fallback.get(r.recommendation)
        flash("AI недостапен — користен е статички fallback.", "warning")
    else:
        content_obj = ai_result
        flash("AI објаснувањето е успешно генерирано.", "success")

    ai = AIAdvice(quiz_result_id=r.id, content=json.dumps(content_obj, ensure_ascii=False))
    session.add(ai)
    session.commit()
    return redirect(url_for("result_detail", result_id=r.id))

if __name__ == "__main__":
    app.run()
