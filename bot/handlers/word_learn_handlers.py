from telegram import send_message, edit_message_keyboard
from services.user_service import *
from services.word_service import *
from sqlalchemy.orm import Session
from entities.keyboards import *
from db.config import redis_client
import json
import random
from entities.models import Words
from sqlalchemy import func
from handlers.redis_handlers import *
from datetime import date
from handlers.word_repeat_handlers import *

# Функция проверки дневного лимита слов
async def check_daily_limit(tg_id: int):
    daily = await get_daily(tg_id=tg_id)
    today = str(date.today())

    if daily and daily.get("last_date") == today:
        return True
    
    return False


# Отправка следующего слова
async def send_next_word(tg_id: int, db: Session):
    session = await get_session(tg_id=tg_id)

    if not session:
        return await send_message(chat_id=tg_id, text="Сессия истекла")
    index = session["current_index"]
    words = session["words"]

    if index >= len(words):
        return await send_message(chat_id=tg_id, text="Поздравляю ты прошел все слова!")
    
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
                    "callback_data": f"answer_learn_{word_id}_{w}"
                }
                for w in options[i:i+2]
            ] 
            for i in range(0, len(options), 2)
        ]
    }

    await send_message(
        chat_id=tg_id, 
        text=f"Переведи слово:  {word['word']}\n Пример: {word['example']}", 
        reply_markup=keyboard
    )


# Обработчик количества слов
async def handle_set_words(callback, db: Session):
    tg_id = callback["from"]["id"]
    word_count = int(callback["data"].replace("set_word_count_", ""))

    if await check_daily_limit(tg_id=tg_id):
        return {
            "chat_id": tg_id,
            "text": "Ты уже прошел сегодняшние все слова, возвращайся завтра за новыми"
        }
    
    words = UserService.get_daily_words(db=db, tg_id=tg_id, word_count=word_count)

    session_data = {
        "words": words,
        "current_index": 0
    }

    await redis_client.set(f"session:{tg_id}", value=json.dumps(session_data), ex=3600)

    await send_message(chat_id=tg_id, text=f"Отлично, сегодня мы изучим {word_count} слов!")

    await send_next_word(tg_id=tg_id, db=db)
    
    return


# Обработка ответа на слово
async def handle_answer(callback, db: Session):
    tg_id = callback["from"]["id"]
    answer = callback["data"].replace("answer_", "")
    mode, word_id, selected = answer.split("_", 2) 

    await edit_message_keyboard(chat_id=tg_id, message_id=callback["message"]["message_id"], reply_markup=None)

    if mode == "repeat":
        session = await get_repeat_session(tg_id=tg_id)
    else:
        session = await get_session(tg_id=tg_id)

    if not session:
        return await send_message(chat_id=tg_id, text="Сессия истекла...")

    word = session["words"][session["current_index"]]
    correct_translation = word["translation"]

    is_correct = selected == correct_translation

    user = db.query(User).filter(User.telegram_id == tg_id).first()

    user_word = db.query(User_words).filter(
        User_words.user_id == user.id,
        User_words.word_id == int(word_id)
    ).first()

    if is_correct:

        if not user_word:
            WordService.save_word_to_db(db=db, tg_id=tg_id, word_id=int(word_id))

        await send_message(chat_id=tg_id, text="✅ Правильно!")

    else:
        await send_message(
            chat_id=tg_id,
            text=f"❌ Неправильно\nПравильный ответ: {correct_translation}"
        )

        if user_word:
            WordService.process_answer(db=db, word=user_word, correct=False)

    session["current_index"] += 1

    if session["current_index"] >= len(session["words"]):
        if mode == "repeat":
            await redis_client.delete(f"repeat:{tg_id}")
        else:
            await redis_client.delete(f"session:{tg_id}")

        await finish_learning(tg_id=tg_id)
        
        return await send_message(
            chat_id=tg_id,
            text="Поздравляю, ты прошел все слова!"
        )
        
    
    if mode == "repeat":
        await set_repeat_session(tg_id=tg_id, session=session)
        return await send_word_repeat(tg_id=tg_id, db=db)
    
    else:
        await update_session(tg_id=tg_id, session=session)

        return await send_next_word(tg_id=tg_id, db=db)
    


