from fastapi import FastAPI, Request, Depends
from config import settings
import httpx
from contextlib import asynccontextmanager
from schemas import UserCreateSchema
from database import get_db
from sqlalchemy.orm import Session
from user_service import UserService
from keyboards import Level_keyboard, Mode_keyboard


# Жизненный цикл бота (Выполняется при старте и выключении сервера)
@asynccontextmanager 
async def lifespan(app: FastAPI):
    webhook_url = settings.get_webhook()
    async with httpx.AsyncClient() as client:
        await client.get(f"https://api.telegram.org/bot{settings.BOT_TOKEN}/setWebhook?url={webhook_url}")

    yield

    print("Выключаемся...")


app = FastAPI(lifespan=lifespan)


# Отправка сообщения пользователю 
async def send_message(chat_id: int, text: str, reply_markup: dict = None):
    url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup

    async with httpx.AsyncClient() as client:   
        await client.post(url, json=payload)

# Функция подтверждения нажатия кнопки (Чтобы убрать анимацию загрузки в тг)
async def answer_callback(callback_id: int):
    url = f"https://telegram.org/bot{settings.BOT_TOKEN}/answerCallbackQuery"
    async with httpx.AsyncClient() as client:
        await client.post(url, json={"callback_query_id": callback_id})


# ОСНОВНОЙ ЭНДПОИНТ ДЛЯ ПРИЕМА СООБЩЕНИЙ В ТГ
@app.post("/webhook")
async def webhook(req: Request, db: Session = Depends(get_db)):
    data = await req.json()

    if "callback_query" in data: # Если пользователь нажал кнопку, выполняем действие
        callback = data["callback_query"]
        await answer_callback(callback["id"])

        tg_id = callback["from"]["id"]
        action = callback["data"]
        print(action)
        if action.startswith("set_lvl_"): # Выбор уровня
            level = action.replace("set_lvl_", "")
            UserService.select_level(db=db, tg_id=tg_id, level=level)
            await send_message(tg_id, f"Уровень {level} установлен! Выбери режим:", Mode_keyboard)

        elif action.startswith("set_mode_"): # Выбор режима
            mode = action.replace("set_mode_", "")
            UserService.select_mode(db=db, tg_id=tg_id, mode=mode)
            UserService.complete_register(db=db, tg_id=tg_id) # Подтверждение регистрации
            await send_message(tg_id, f"Режим {mode} выбран! Начинаем обучение.")
        
        
        return {"ok": True} # Завершаем обработку если была выборка

    # Дальше уже если обычное сообщение
    message = data.get("message", {})
    from_info = message.get("from")
    
    if not from_info or "text" not in message:
        return {"ok": True}

    user_data = UserCreateSchema(
        username=from_info.get("username"),
        telegram_id=from_info.get("id"),
        first_name=from_info.get("first_name") 
    )

    user = UserService.create_user(db, user_data)   # Создаем пользователя (В методе есть проверка на существование)

    # Реакция на команду /start
    if message["text"] == "/start":

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

    return {"ok": True}








    
