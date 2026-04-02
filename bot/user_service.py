from sqlalchemy.orm import Session
from schemas import UserCreateSchema
from models import User

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
        if user:
            user.level = level
            db.commit()
            db.refresh(user)

    # Выбор режима
    @staticmethod 
    def select_mode(db: Session, tg_id: int, mode: str):
        user = db.query(User).filter_by(telegram_id=tg_id).first()
        if user:
            user.mode = mode
            db.commit()
            db.refresh(user)

    # Регистрация пользователя
    @staticmethod 
    def complete_register(db: Session, tg_id: int):
        user = db.query(User).filter_by(telegram_id=tg_id).first()
        if user:
            user.is_registered = True
            db.commit()
    
        



    
    
    