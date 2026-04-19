from fastapi import FastAPI, Request, Depends
from db.config import settings
import httpx
from contextlib import asynccontextmanager
from db.database import get_db
from sqlalchemy.orm import Session
from entities.keyboards import *
from handlers.user_handlers import handle_callback, handle_start, handle_create_user
from handlers.dialogue_handlers import handle_message
from telegram import send_message
from db.database import Base, engine


# Жизненный цикл бота (Выполняется при старте и выключении сервера)
@asynccontextmanager 
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    webhook_url = settings.get_webhook()
    async with httpx.AsyncClient() as client:
        await client.get(f"https://api.telegram.org/bot{settings.BOT_TOKEN}/setWebhook?url={webhook_url}")

    yield

    print("Выключаемся...")


app = FastAPI(lifespan=lifespan)


# ОСНОВНОЙ ЭНДПОИНТ ДЛЯ ПРИЕМА СООБЩЕНИЙ В ТГ
@app.post("/webhook")
async def webhook(req: Request, db: Session = Depends(get_db)):
    try:
        data = await req.json()

        if "callback_query" in data: # Если пользователь нажал кнопку, выполняем действие
            response = await handle_callback(callback=data["callback_query"], db=db)

            if response:
                await send_message(chat_id=response["chat_id"], text=response["text"], reply_markup=response.get("keyboard"))
                
            return {"ok": True} # Завершаем обработку если была выборка


        # Дальше уже если обычное сообщение
        message = data.get("message", {})
        from_info = message.get("from")
        
        if not from_info or "text" not in message:
            return {"ok": True}

        user = await handle_create_user(user=from_info, db=db)
        print(message["text"])
        await handle_message(user=user, text=message["text"], db=db)

        # Реакция на команду /start
        if message["text"] == "/start":
            await handle_start(user=user, db=db)

        return {"ok": True}
    
    except Exception as e:
        print("ERROR:", e)
        return {"ok": True}








    
