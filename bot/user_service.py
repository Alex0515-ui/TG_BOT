from sqlalchemy.orm import Session
from schemas import UserCreateSchema
from models import User


class UserService:

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

    
    
    