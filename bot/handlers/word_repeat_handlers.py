from telegram import send_message
from services.word_service import *
from sqlalchemy.orm import Session
from db.config import redis_client
import random
from entities.models import Words
from sqlalchemy import func
from handlers.redis_handlers import *


# Отправка слов на повторение
async def send_word_repeat(tg_id: int, db: Session):
    session = await get_repeat_session(tg_id=tg_id)
    if not session:
        return await send_message(chat_id=tg_id, text="Сессия закончилась")

    index = session["current_index"]
    words = session["words"]

    if index >= len(words):        
        await send_message(chat_id=tg_id, text="Поздравляю, ты повторил все слова!")
        await redis_client.delete(f"repeat:{tg_id}")
        return

    word = words[index]

    random_words = db.query(Words).order_by(func.random()).limit(10).all()
    wrong_translations = [
        w.translation for w in random_words 
        if w.translation != word["translation"]
    ][:3]

    options = wrong_translations + [word["translation"]]
    random.shuffle(options)

    session["options"] = options
    await set_repeat_session(tg_id=tg_id, session=session)
    
    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": opt,
                    "callback_data": f"answer_repeat_{word['id']}_{idx}"
                }
                for idx, opt in enumerate(options[i:i+2], start=i)
            ] for i in range(0, len(options), 2)
        ]
    }
    await send_message(
        chat_id=tg_id, 
        text=f"Переведи слово: {word['word']}\nПример: {word['example']}", 
        reply_markup=keyboard
    )
    

# Начало повторения слов
async def start_repeat_session(tg_id: int, db: Session):
    words = WordService.get_words_to_repeat(db=db, tg_id=tg_id)

    session_data = {
        "words": [
            {
                "id": w.word_id,
                "word": w.word.word,
                "translation": w.word.translation,
                "example": w.word.example
            }
            for w in words
        ],
        "current_index": 0
    }

    await set_repeat_session(tg_id, session_data)

    return await send_word_repeat(tg_id, db)
