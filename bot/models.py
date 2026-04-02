from database import Base
from sqlalchemy import Column, Integer,String, Enum as SQLEnum, BigInteger, func, DateTime, Boolean
from enum import Enum

# Уровни владения англ языком
class Levels(str, Enum):
    A1 = "Beginner"
    A2 = "Elementary"
    B1 = "Pre-intermediate"
    B2 = "Intermediate"
    C1 = "Upper-intermediate"
    C2 = "Advanced"

# Режимы англ: Обычный, Технический(Для работы)
class Mode(str, Enum):
    GENERAL = "general"
    TECH = "tech"

# Основная таблица пользователя
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    username = Column(String, nullable=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    level = Column(SQLEnum(Levels), nullable=True, default=Levels.A1)
    mode = Column(SQLEnum(Mode), nullable=True, default=Mode.GENERAL)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_registered = Column(Boolean, default=False)

    def __repr__(self):
        return f"User: telegram_id:{self.telegram_id}, level: {self.level}"






