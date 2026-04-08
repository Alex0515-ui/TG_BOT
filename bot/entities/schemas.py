from pydantic import BaseModel
from typing import Optional


# Валидация для создания пользователя
class UserCreateSchema(BaseModel):
    first_name: str
    telegram_id: int
    username: Optional[str] = None

