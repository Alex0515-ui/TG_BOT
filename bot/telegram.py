import httpx
from db.config import settings

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


# Исчезнование кнопок после выбора
async def edit_message_keyboard(chat_id:int, message_id: int, reply_markup: dict = None):
    url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/editMessageReplyMarkup"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id
    }
    if reply_markup is not None:
        payload["reply_markup"] = reply_markup
    
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)


# Одноразовая функция, для удаления кнопок справа от поля ввода сообщения
async def remove_reply_keyboard(chat_id: int):
    url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/editMessageReplyMarkup"

    payload = {
        "chat_id": chat_id,
        "text": " ",
        "reply_markup": {
            "remove_keyboard": True
        }
    }

    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)