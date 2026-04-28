from db.config import redis_client
from telegram import send_message
from entities.models import User
from entities.keyboards import Menu_keyboard
from handlers.redis_handlers import get_chat_dialogue, get_daily_dialogue, get_session_practise
from AI.ai_dialogue import send_chat_message
from sqlalchemy.orm import Session
import json
from datetime import date
from handlers.practise_handlers import handle_practise_answer

# Функция проверки дневного лимита слов
async def check_daily_limit_dialogue(tg_id: int):
    daily = await get_daily_dialogue(tg_id=tg_id)
    today = str(date.today())

    if daily and daily.get("last_date") == today:
        return True
        
    return False

# Начала диалога с ИИ
async def start_dialogue(tg_id: int):
    limit = await check_daily_limit_dialogue(tg_id=tg_id)

    if limit:
        return await send_message(chat_id=tg_id, text="Ты уже поговорил с ИИ ассистентом сегодня\nМожешь поговорить с ним завтра заново!")
    
    await redis_client.set(
        f"dialogue:{tg_id}", 
        json.dumps({
            "messages":[], 
            "active": True, 
            "limit": 10, 
            "used": 0
        })
    )
    
    return await send_message(chat_id=tg_id, text="Hello! Write something and we can talk about it")


# Обработчик текстовых команд и сообщениям для ИИ собеседника
async def handle_message(user: User, text: str, db: Session):
    if text == "Главное меню":
        return await send_message(chat_id=user.telegram_id, text="Главное меню", reply_markup=Menu_keyboard)
    
    dialogue = await get_chat_dialogue(tg_id=user.telegram_id)

    if dialogue:
        return await send_chat_message(tg_id=user.telegram_id, user_text=text, db=db)
    
    practise = await get_session_practise(tg_id=user.telegram_id)
    
    if practise:
        return await handle_practise_answer(tg_id=user.telegram_id, user_text=text)

    return await send_message(chat_id=user.telegram_id, text="Я не понимаю вашу команду")

