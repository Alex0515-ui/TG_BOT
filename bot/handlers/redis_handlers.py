import json
from db.config import redis_client
from datetime import date


# ============ ИЗУЧЕНИЕ СЛОВ ===============

# Получение сессии из Redis
async def get_session(tg_id: int):
    data = await redis_client.get(f"session:{tg_id}")
    return json.loads(data) if data else None

# Обновление сессии
async def update_session(tg_id: int, session: dict):
    await redis_client.set(f"session:{tg_id}", json.dumps(session), ex=3600)


# ============ ДНЕВНОЙ ЛИМИТ ===============================


# Получение сессии последней даты изучения слов
async def get_daily(tg_id: int):
    data = await redis_client.get(f"daily:{tg_id}")
    return json.loads(data) if data else None

# Обновление сессии последней даты изучения слов
async def set_daily(tg_id: int, date: str):
    await redis_client.set(f"daily:{tg_id}", json.dumps({"last_date": date}), ex=172800)

# Лимит слов в в день
async def finish_learning(tg_id:int):
    today = str(date.today())
    data = {
        "last_date": today
    }
    await redis_client.set(f"daily:{tg_id}", value=json.dumps(data), ex=172000)

# Получение дневного лимита диалога с ИИ
async def get_daily_dialogue(tg_id:int):
    data = await redis_client.get(f"daily_dialogue:{tg_id}")
    if data:
        return json.loads(data)
    
# Установка дневного лимита с ИИ диалог
async def set_daily_dialogue(tg_id:int, date: str):
    await redis_client.set(f"daily_dialogue:{tg_id}", json.dumps({"last_date": date}), ex=172800)


# ======== ПОВТОРЕНИЕ СЛОВ ==============================


# Получение сессии повторения слов
async def get_repeat_session(tg_id: int):
    data = await redis_client.get(f"repeat:{tg_id}")
    return json.loads(data) if data else None

# Обновление сессии повторения слов
async def set_repeat_session(tg_id: int, session: dict):
    await redis_client.set(f"repeat:{tg_id}", json.dumps(session), ex=18000)


# ================ ДИАЛОГ С ИИ ===================


# Получение истории чата
async def get_chat_dialogue(tg_id:int):
    data = await redis_client.get(f"dialogue:{tg_id}")
    if data:
        return json.loads(data)

# Добавление в историю чата сообщения
async def save_chat_dialogue(tg_id:int, history: dict):
    await redis_client.set(f"dialogue:{tg_id}", json.dumps(history))


# ============ ПРАКТИКА СЛОВ  =========

# Получение временного хранилища слов
async def get_practise(tg_id: int):
    data = await redis_client.get(f"practise:{tg_id}")
    if data:
        return json.loads(data)
    
# Временное хранилише слов
async def set_practise(tg_id: int, data):
    await redis_client.set(f"practise:{tg_id}", json.dumps(data))

# Получение сессии для практики
async def get_session_practise(tg_id: int):
    data = await redis_client.get(f"practise_session:{tg_id}")
    if data:
        return json.loads(data)

# Сессия слов для практики
async def set_session_practise(tg_id: int, data):
    await redis_client.set(f"practise_session:{tg_id}", json.dumps(data), ex=21600)












