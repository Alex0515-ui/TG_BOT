from groq import Groq
from db.config import settings
import json
from AI.ai_prompts import GENERATION_SYSTEM_PROMPT, CHECK_SYSTEM_PROMPT


client = Groq(api_key=settings.GROQ_API_KEY)

# Генерация предложений
async def generate_sentences(words: list[str]):

    prompt = "Words:\n" + "\n".join(words)

    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": GENERATION_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_completion_tokens=1500,
        top_p=1,
    )

    response_text = completion.choices[0].message.content

    try:
        data = json.loads(response_text)
        return data.get("data", [])
    
    except Exception:
        return None

# Просто обертка для сообщения в ИИ
def build_check_prompt(word: str, ru_sentences: list[str], user_answer: str):
    print(ru_sentences)
    ru_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(ru_sentences)])

    return f"""Target word: {word}

    Russian sentences:
    {ru_text}

    User answer:
    {user_answer}
    """

# Проверка корректности ответа пользователя
async def check_translation(word: str, ru_sentences: list[str], user_answer: str):

    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": CHECK_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": build_check_prompt(word, ru_sentences, user_answer)
            }
        ],
        temperature=0.3,
        max_completion_tokens=500,
    )

    return completion.choices[0].message.content