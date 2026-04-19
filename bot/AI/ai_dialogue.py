from groq import Groq
from db.config import settings
from handlers.redis_handlers import get_chat_dialogue, save_chat_dialogue, set_daily_dialogue
from telegram import send_message
from sqlalchemy.orm import Session
from entities.models import User
from db.config import redis_client
from datetime import date


MAX_HISTORY = 10

client = Groq(api_key=settings.GROQ_API_KEY)

# Отправка сообщение ИИ и получение ответа во время диалога
async def send_chat_message(tg_id:int, user_text: str, db: Session):
    user = db.query(User).filter(User.telegram_id == tg_id).first()

    if not user:
        return None
    
    # Поведение ИИ
    SYSTEM_PROMPT = f"""You're a friendly communication assistant.

    User English level: {user.level}

    Rules:
    - Adapt vocabulary to user's level
    - If level is low, use simple sentences
    - If level is high, speak more naturally and complex
    """

    history = await get_chat_dialogue(tg_id=tg_id)

    if history.get("used", 0) >= history.get("limit", 10):
        today = str(date.today())
        await redis_client.delete(f"dialogue:{tg_id}")

        await set_daily_dialogue(tg_id=tg_id, date=today)
        return await send_message(chat_id=user.telegram_id, text="Лимит диалога исчерпан, возвращайся завтра")

    # Структурируем сообщение
    messages = [
        {"role":"system", "content": SYSTEM_PROMPT},
        *history["messages"],
        {"role":"user", "content": user_text}
    ]

    # Сам запрос В ИИ
    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages,
        temperature=1,
        max_completion_tokens=800,
        top_p=1,
        reasoning_effort="low",
        stream=True,
    )

    response_text = ""  

    for chunk in completion:
        content = chunk.choices[0].delta.content or ""
        response_text += content
        print(content, end="")

    # Сохраняем всю историю диалога
    history["messages"].append({"role": "user", "content": user_text})
    history["messages"].append({"role": "assistant", "content": response_text})

    history["messages"] = history["messages"][-MAX_HISTORY:]
    history["used"] += 1

    await save_chat_dialogue(tg_id=tg_id, history=history)

    # Возвращаем ответ пользователю
    return await send_message(chat_id=tg_id, text=response_text)

    

