from google import genai
from google.genai import types
import json
from db.database import SessionLocal
from entities.models import Words
from db.config import settings
from sqlalchemy.orm import Session
import time

client = genai.Client(api_key=settings.GEMINI_API_KEY)

# Запрос в Gemini API
def get_words_from_ai(prompt: str):
    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            response = client.models.generate_content(
                model="gemini-3-flash-preview", 
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2
                )
            )
            return json.loads(response.text)
        except Exception as e:
            if "429" in str(e):
                wait = 70
                print(f"Limit reached. Attempt {attempt+1}/{max_attempts}. Slepping for {wait} seconds")
                time.sleep(wait)
            else:
                raise e
    return None



# Функция для заполнения словаря в БД
def fill_database():

    db: Session = SessionLocal()
    TOPICS = [
        "System Architecture", "Database Management", "Infrastructure & DevOps", "Daily Conversation", 
        "Business Meeting", "Network Communications", "Software Engineering", "Application Security", 
        "Performance & Scaling", "Cloud Computing", "Distributed Systems", "Site Reliability", 
        "API & Integration", "Operating Systems", "Data Processing", "Project Management", 
        "Technical Leadership"
    ]
    LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]

    tasks = []

    for level in LEVELS:

        tasks.append({
            "prompt": f"Give me 50 English words for everyday use of level {level}. "
                      f"Format: list of objects {{'word', 'translation', 'example', 'level', 'type'}}"
                      f"Translation must be in RUSSIAN. ",
            "level" : level,
            "type": "GENERAL"
        })

    tasks.append({
        "prompt": f"Give me 50 technical English words (levels B1-C2) for reading documentation about: {TOPICS}. "
                  f"Format: list of objects {{'word', 'translation', 'example', 'level', 'type'}}"
                  f"Translation must be in RUSSIAN. ",
        "level": "B2",
        "type": "TECH"
    })

    for task in tasks:
        try:
            print(f"Requesting {task["type"]} for level {task.get("level", "B1-C2")}...")
            data = get_words_from_ai(task["prompt"])

            if not data:
                print(f"Cannot get data for {task["level"]} after all attempts...")
                continue

            words_count = 0

            for word in data:
                word_str = word["word"].lower().strip()

                exists = db.query(Words).filter(Words.word==word_str).first()

                if not exists:
                    try:
                        new_word = Words(
                            word=word_str,
                            translation=word["translation"],
                            example=word["example"],
                            level=word.get("level", task["level"]),
                            type=task["type"]
                        )

                        db.add(new_word)
                        words_count += 1

                    except Exception as e:
                        print(f"Word validation error {word_str}: {e}")

            db.commit()
            print(f"Succesfully added {words_count} new words!")
            print("Waiting 20 seconds for API Quota")
            time.sleep(20)

        except Exception as e:
            if "429" in str(e):
                print("Limit reached. Sleeping for 60 seconds")
                time.sleep(70)
            else:
                print(f"Error processing the request: {e}")
            db.rollback()
            
    db.close()
    print("Database filled!")


if __name__ == "__main__":
    fill_database()



