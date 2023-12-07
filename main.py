# main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional

app = FastAPI()

DATABASE_URL = "postgresql://postgres:Reubjeon512@localhost/fastapi"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Определение моделей
Base = declarative_base()

# Создание таблиц
Base.metadata.create_all(bind=engine)

# Для запуска приложения используйте следующую команду:
# uvicorn main:app --reload
