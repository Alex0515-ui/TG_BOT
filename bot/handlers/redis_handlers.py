import json
from db.config import redis_client


# Получение сессии из Redis
async def get_session(tg_id: int):
    data = await redis_client.get(f"session:{tg_id}")
    return json.loads(data) if data else None

# Обновление сессии
async def update_session(tg_id: int, session: dict):
    await redis_client.set(f"session:{tg_id}", json.dumps(session), ex=3600)

# Получение сессии последней даты изучения слов
async def get_daily(tg_id: int):
    data = await redis_client.get(f"daily:{tg_id}")
    return json.loads(data) if data else None

# Обновление сессии последней даты изучения слов
async def set_daily(tg_id: int, date: str):
    await redis_client.set(f"daily:{tg_id}", json.dumps({"last_date": date}), ex=172800)


