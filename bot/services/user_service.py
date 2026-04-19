from sqlalchemy.orm import Session
from entities.schemas import UserCreateSchema
from entities.models import User, User_words, Words
from sqlalchemy import func
from telegram import send_message
from entities.keyboards import Main_menu_keyboard


class UserService:

    # Создание пользователя
    @staticmethod  
    def create_user(db: Session, data: UserCreateSchema):
        user = db.query(User).filter_by(telegram_id=data.telegram_id).first()

        if user:
            print(f"Пользователь {user.telegram_id} найден в базе.")
            return user
        
        print(f"Создаем нового пользователя {data.telegram_id}")
        user = User(
            username=data.username, 
            telegram_id=data.telegram_id,
            first_name=data.first_name
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    # Выбор уровня
    @staticmethod 
    def select_level(db: Session, tg_id: int, level: str):
        user = db.query(User).filter_by(telegram_id=tg_id).first()
        print("Уровень установлен")
        if user:
            user.level = level
            db.commit()
            db.refresh(user)

    # Выбор режима
    @staticmethod 
    def select_mode(db: Session, tg_id: int, mode: str):
        user = db.query(User).filter_by(telegram_id=tg_id).first()
        print("Мод установлен")
        if user:
            user.mode = mode
            db.commit()
            db.refresh(user)

    # Регистрация пользователя
    @staticmethod 
    async def complete_register(db: Session, tg_id: int):
        user = db.query(User).filter_by(telegram_id=tg_id).first()
        if user.is_registered == False:
            await send_message(
                chat_id=user.telegram_id, 
                text="Справа от поля ввода сообщения у тебя будет кнопка главного меню", 
                reply_markup=Main_menu_keyboard
            )
        if user:
            user.is_registered = True
            db.commit()
    
    # Получение ежедневных слов
    @staticmethod
    def get_daily_words(db: Session, tg_id: int, word_count: int):
        user = db.query(User).filter_by(telegram_id=tg_id).first()
        if not user:
            return None
        
        excluded_words = db.query(User_words.word_id).where(User_words.user_id == user.id)
        result = []

        words = db.query(Words).filter(
            ~Words.id.in_(excluded_words), 
            Words.level==user.level, Words.type==user.mode
        ).order_by(func.random()).limit(word_count).all()

        if not words:
            return []
        for word in words:
            result.append({"id": word.id, "word": word.word, "translation": word.translation, "example": word.example})

        return result
    

    



        



    
    
    