from telegram import send_message
from services.user_service import *
from services.word_service import *
from sqlalchemy.orm import Session
from entities.keyboards import *
from entities.models import User
from handlers.word_learn_handlers import *
from handlers.redis_handlers import get_session
from handlers.word_repeat_handlers import *
from handlers.dialogue_handlers import *
from handlers.practise_handlers import *

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
async def handle_start(user: User, db: Session): 
    
    if user.is_registered:
            await send_message(chat_id=user.telegram_id, text=f"С возвращением {user.first_name}!")
            await send_message(chat_id=user.telegram_id, text="Главное меню:", reply_markup=Menu_keyboard)
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

# Обработчик начала обучения
async def start_learning(tg_id: int, db: Session):
    user = db.query(User).filter(User.telegram_id==tg_id).first()

    session = await get_session(user.telegram_id)
    
    if not user.is_registered:
        return await send_message(chat_id=user.telegram_id, text="Сначала выбери уровень и режим", reply_markup=Level_keyboard)

    if session:
        return await send_next_word(tg_id=user.telegram_id, db=db)
    
    if await check_daily_limit(tg_id=user.telegram_id):
        return await send_message(chat_id=user.telegram_id, text="Ты уже прошел сегодняшние все слова, возвращайся завтра за новыми")
        
    
    return await send_message(chat_id=user.telegram_id, text="Выбери режим на сегодня:", reply_markup=Mode_keyboard)
    
    

        
    
# Главный обработчик действий
async def handle_callback(callback, db: Session):
    action = callback["data"]
    tg_id = callback["from"]["id"]

    if action.startswith("set_lvl_"):
        return await handle_set_level(callback=callback, db=db)

    elif action.startswith("set_mode_"):
        return await handle_set_mode(callback=callback, db=db)

    elif action.startswith("set_word_count_"):
        return await handle_set_words(callback=callback, db=db)
    
    elif action.startswith("answer_"):
        return await handle_answer(callback=callback, db=db) 
    
    elif action.startswith("set_repeat"):
        return await start_repeat_session(tg_id=tg_id, db=db)

    elif action.startswith("choose_level"):
        return await send_message(chat_id=tg_id, text="Выбери уровень:", reply_markup=Level_keyboard)

    elif action.startswith("choose_mode"):
        return await send_message(chat_id=tg_id, text="Выбери режим:", reply_markup=Mode_keyboard)
    
    elif action.startswith("set_learning"):
        return await start_learning(tg_id=tg_id, db=db)
    
    elif action.startswith("start_dialogue"):
        return await start_dialogue(tg_id=tg_id)
    
    elif action.startswith("set_practise_yes"):
        return await Yes_practise(callback=callback, tg_id=tg_id)
    
    elif action.startswith("set_practise_no"):
        return await No_practise(callback=callback, tg_id=tg_id)
    
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
    await UserService.complete_register(db=db, tg_id=tg_id) 
    
    reached_limit = await check_daily_limit(tg_id=tg_id)

    if reached_limit:
        return {
            "chat_id": tg_id,
            "text": "Ты уже прошел сегодняшние все слова, возвращайся завтра за новыми",
            "keyboard": None
        }
    
    return {
        "chat_id": tg_id,
        "text": f"Режим {mode} выбран! Начинаем обучение. Выбери количество слов для изучения сегодня:", 
        "keyboard": Word_count_keyboard
    }






