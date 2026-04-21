from db.database import Base
import pytest
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Создаем фейковую БД для ТЕСТОВ
@pytest.fixture
def db():

    url = "sqlite:///:memory:"
    engine = create_engine(url)

    test_session_local = sessionmaker(bind=engine)

    Base.metadata.create_all(bind=engine)

    session = test_session_local()

    yield session

    session.close()
