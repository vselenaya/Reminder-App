import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local_backend.db")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Функция будет отвечать за создание таблиц.
def init_db():
    # Важно: импортируем модели здесь, чтобы убедиться,
    # что они зарегистрированы в Base.metadata перед созданием таблиц.
    from . import models
    Base.metadata.create_all(bind=engine)
