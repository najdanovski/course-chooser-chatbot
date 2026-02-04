import json
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()  

MODEL_NAME = "gemini-3-flash-preview"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable не е поставена!")


def generate_explanation(answers: dict, recommendation: str) -> dict | None:

    if not GEMINI_API_KEY:
        print("GEMINI_API_KEY недостасува")
        return None

    prompt = (
        "Ти си пријателски советник за избор на кариерни патеки.\n"
        "Објасни зошто курсот е добар избор.\n"
        "Врати САМО валиден JSON со полиња:\n"
        "title (string), explanation (string), tips (array of strings).\n\n"
        "Кориснички одговори:\n"
    )
    
    for k, v in answers.items():
        prompt += f"{k}: {v}\n"
    prompt += f"Препорачан курс: {recommendation}"

    client = genai.Client(api_key=GEMINI_API_KEY)

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        text = (response.text or "").strip()
        
        if text.startswith("```"):
            text = text.split("```")[1]

        return json.loads(text)
    except Exception as e:
        print("AI грешка:", e)
        return None
