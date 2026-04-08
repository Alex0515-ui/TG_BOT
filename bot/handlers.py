from telegram import send_message
from services.user_service import *
from services.word_service import *
from sqlalchemy.orm import Session
from entities.keyboards import *
from entities.models import User

# Обработчик создания пользователя
async def handle_create_user(user, db: Session):
    user_data = UserCreateSchema(
        username=user.get("username"),
        telegram_id=user.get("id"),
        first_name=user.get("first_name") 
    )

    user = UserService.create_user(db, user_data)   # Создаем пользователя (В методе есть проверка на существование)
    return user


# Обработчик начала работы бота /start
async def handle_start( user: User):
    if user.is_registered:
            await send_message(chat_id=user.telegram_id, text=f"С возвращением {user.first_name}! Выбери режим на сегодня:", reply_markup=Mode_keyboard)
    else:
        await send_message(
            chat_id=user.telegram_id, 
            text=f"Привет, {user.first_name}! Я бот для изучения английского."
        )
        
        await send_message(
            chat_id=user.telegram_id, 
            text="Выберите свой уровень английского:",
            reply_markup=Level_keyboard     
        )

# Главный обработчик действий
async def handle_callback(callback, db: Session):
    action = callback["data"]

    if action.startswith("set_lvl_"):
        return await handle_set_level(callback=callback, db=db)

    elif action.startswith("set_mode_"):
        return await handle_set_mode(callback=callback, db=db)

    elif action.startswith("set_word_count"):
        return await handle_set_words(callback=callback, db=db)


# Обработчик установки уровня пользователя
async def handle_set_level(callback, db: Session):
    tg_id = callback["from"]["id"]
    level = callback["data"].replace("set_lvl_", "")

    UserService.select_level(db=db, tg_id=tg_id, level=level)

    return {
        "chat_id": tg_id,
        "text": f"Уровень {level} установлен! Теперь выбери сегодняшний режим обучения:",
        "keyboard": Mode_keyboard
    }

# Обработчик установки режима
async def handle_set_mode(callback, db: Session):
    tg_id = callback["from"]["id"]
    mode = callback["data"].replace("set_mode_", "")

    UserService.select_mode(db=db, tg_id=tg_id, mode=mode)
    UserService.complete_register(db=db, tg_id=tg_id)
    return {
        "chat_id": tg_id,
        "text": f"Режим {mode} выбран! Начинаем обучение. Выбери количество слов для изучения сегодня:", 
        "keyboard": Word_count_keyboard
    }

# Обработчик количества слов
async def handle_set_words(callback, db: Session):
    tg_id = callback["from"]["id"]
    word_count = int(callback["data"].replace("set_word_count_", ""))

    words = UserService.get_daily_words(db=db, tg_id=tg_id, word_count=word_count)
    for word in words:
        await send_message(
            chat_id=tg_id,
            text=f"{word['word']}\n\nПример: {word['example']}"
        )
    return {
        "chat_id": tg_id,
        "text": f"Отлично, сегодня мы изучим {word_count} слов!"
    }

