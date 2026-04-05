from database import Base
from sqlalchemy import Column, Integer,String, Enum as SQLEnum, BigInteger, func, DateTime, Boolean, ForeignKey
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


# Словарь слов
class Words(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, unique=True, index=True, nullable=False)

    translation = Column(String, nullable=False)
    example = Column(String, nullable=False)

    level = Column(SQLEnum(Levels), nullable=False)
    type = Column(SQLEnum(Mode), nullable=False)

    def __repr__(self):
        return f"{self.word}, ({self.level}, {self.type})"

# Статус слова
class Word_Status(Enum):
    NEW = "new"
    LEARNING = "learning"
    LEARNED = "learned"

# Таблица слов в обучении каждого пользователя
class User_words(Base):
    __tablename__ = "user_words"

    id = Column(Integer, primary_key=True, index=True)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    status = Column(SQLEnum(Word_Status), default=Word_Status.NEW)

    next_review_date = Column(DateTime(timezone=True))  # Следующее повторение слова
    repetition_stage = Column(Integer, default=0)   # Для отслеживания прогресса






