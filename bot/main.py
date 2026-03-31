from fastapi import FastAPI, Request
from config import settings
import httpx
from contextlib import asynccontextmanager

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
async def webhook(req: Request):
    data = await req.json()

    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text")

    if not chat_id:
        return {"ok": True}
    if text == "/start":
        await send_message(chat_id=chat_id, text="Привет! Я ваш Telegram бот.")
    else:
        await send_message(chat_id=chat_id, text=f"Ты написал: {text}")

    return {"ok": True}



    
