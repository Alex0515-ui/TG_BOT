from fastapi import FastAPI, Request, Depends
from config import settings
import httpx
from contextlib import asynccontextmanager
from schemas import UserCreateSchema
from database import get_db
from sqlalchemy.orm import Session
from user_service import UserService


@asynccontextmanager
async def lifespan(app: FastAPI):
    webhook_url = settings.get_webhook()
    async with httpx.AsyncClient() as client:
        await client.get(f"https://api.telegram.org/bot{settings.BOT_TOKEN}/setWebhook?url={webhook_url}")

    yield

    print("Выключаемся...")


app = FastAPI(lifespan=lifespan)


async def send_message(chat_id: int, text: str):
    url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage"

    async with httpx.AsyncClient() as client:
        await client.post(url, json={
            "chat_id": chat_id,
            "text": text
        })


@app.post("/webhook")
async def webhook(req: Request, db: Session = Depends(get_db)):
    data = await req.json()
    message = data.get("message", {})
    from_info = message.get("from")

    if not from_info or "text" not in message:
        return {"ok": True}

    user_data = UserCreateSchema(
        username=from_info.get("username"),
        telegram_id=from_info.get("id"),
        first_name=from_info.get("first_name") 
    )

    user = UserService.create_user(db, user_data)

    if message["text"] == "/start":
        await send_message(
            chat_id=user.telegram_id, 
            text=f"Привет, {user.first_name}! Я бот для изучения английского языка."
        )

    return {"ok": True}




    
