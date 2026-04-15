from celery_app import celery_app
from sqlalchemy.orm import Session
from datetime import date, datetime, timezone
from entities.models import User_words, User, Word_Status
from telegram import send_message
from db.database import SessionLocal
import asyncio
from entities.keyboards import Repeat_word_keyboard

# Отправка уведомлений о повторениях слов
async def send_repeat_notifications(users):
    tasks = []
    for user in users:
        tasks.append(send_message(
                chat_id=user.telegram_id, 
                text=f"Привет, {user.first_name}!\nДавай повторим прошлые слова", 
                reply_markup=Repeat_word_keyboard
            )
        )

    await asyncio.gather(*tasks)

# Проверка слов на повторение
@celery_app.task
def Check_repetitions():
    with SessionLocal() as db:
        now = datetime.now(timezone.utc)
        
        users_ids = db.query(User_words.user_id).filter(
            User_words.next_review_date <= now, 
            User_words.status == Word_Status.LEARNING
        ).distinct().all()

        user_ids = [u[0] for u in users_ids]
        users = db.query(User).filter(User.id.in_(user_ids))

        if users:
            asyncio.run(send_repeat_notifications(users))
