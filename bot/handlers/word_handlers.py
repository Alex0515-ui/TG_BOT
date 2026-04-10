from telegram import send_message
from services.user_service import *
from services.word_service import *
from sqlalchemy.orm import Session
from entities.keyboards import *
from db.config import redis_client
import json
import random
from entities.models import Words
from sqlalchemy import func


# Получение сессии из Redis
async def get_session(tg_id: int):
    data = await redis_client.get(f"session:{tg_id}")
    if not data:
        return None
    return json.loads(data)

# Обновление сессии
async def update_session(tg_id: int, session: dict):
    await redis_client.set(f"session:{tg_id}", json.dumps(session), ex=3600)

# Отправка следующего слова
async def send_next_word(tg_id: int, db: Session):
    session = await get_session(tg_id=tg_id)

    if not session:
        return 
    index = session["current_index"]
    words = session["words"]
    print(words)
    if index >= len(words):
        await send_message(chat_id=tg_id, text=f"Поздравляю ты прошел все слова!")
        return

    word = words[index]
    random_words = db.query(Words).order_by(func.random()).limit(10).all()

    wrong_translations = [w.translation for w in random_words if w.translation != word["translation"]][:3]

    options = wrong_translations + [word["translation"]]
    random.shuffle(options)
    word_id = word["id"]
    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": w,
                    "callback_data": f"answer_{word_id}_{w}"
                }
            ] for w in options
        ]
    }

    await send_message(
        chat_id=tg_id, 
        text=f"Переведи слово:\n\n{word['word']}", 
        reply_markup=keyboard
    )


# Обработчик количества слов
async def handle_set_words(callback, db: Session):
    tg_id = callback["from"]["id"]
    word_count = int(callback["data"].replace("set_word_count_", ""))

    words = UserService.get_daily_words(db=db, tg_id=tg_id, word_count=word_count)
    print(words)
    session_data = {
        "words": words,
        "current_index": 0
    }

    await redis_client.set(f"session:{tg_id}", value=json.dumps(session_data), ex=3600)

    await send_next_word(tg_id=tg_id, db=db)
    
    return {
        "chat_id": tg_id,
        "text": f"Отлично, сегодня мы изучим {word_count} слов!"
    }

# Обработчик кнопки "Запомнил" после неверного ответа
async def handle_remember(callback, db: Session):
    tg_id = callback["from"]["id"]
    session = await get_session(tg_id=tg_id)

    if not session:
        return
    
    session["current_index"] += 1
    await update_session(tg_id=tg_id, session=session)
    await send_message(chat_id=tg_id, text="Отлично, идем дальше!")
    await send_next_word(tg_id=tg_id, db=db)

    return {"chat_id": tg_id}

# Обработчик кнопки повторения слова после неверного ответа
async def handle_repeat(callback, db: Session):
    tg_id = callback["from"]["id"]
    session = await get_session(tg_id=tg_id)

    if not session:
        return
    
    await send_message(chat_id=tg_id, text="Попробуй еще разок")
    await send_next_word(tg_id=tg_id, db=db)


# Обработка ответа
async def handle_answer(callback, db: Session):
    tg_id = callback["from"]["id"]
    print(callback)
    answer = callback["data"].replace("answer_", "")
    print(answer)
    word_id, selected = answer.split("_", 1) 

    session = await get_session(tg_id=tg_id)
    if not session:
        await send_message(chat_id=tg_id, text="К сожалению сессия уже истекла...")
    print(session)
    word = session["words"][session["current_index"]]
    correct_translation = word["translation"]

    if selected == correct_translation:
        WordService.save_word_to_db(db=db, tg_id=tg_id, word_id=int(word_id))
        session["current_index"] += 1
        await update_session(tg_id=tg_id, session=session)

        await send_message(chat_id=tg_id, text="Правильно!")
        await send_next_word(tg_id=tg_id, db=db)
    
    else:
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "Запомнил ✅", "callback_data": f"remember_{word_id}"},
                    {"text": "Еще раз 🔁", "callback_data": f"repeat_{word_id}"}
                ]
            ]
        }
        return {
            "chat_id": tg_id,
            "text": f"❌ Неправильно\nПравильный ответ: {correct_translation}",
            "keyboard": keyboard
        }
