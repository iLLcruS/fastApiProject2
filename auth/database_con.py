from datetime import datetime
from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column
from sqlalchemy import Boolean, ForeignKey, Integer, String, func, select, TIMESTAMP

from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER
from models.user import role

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
Base: DeclarativeBase = declarative_base()


class User(SQLAlchemyBaseUserTable[int], Base):
    id: Mapped[int] = mapped_column(
        Integer(),
        unique=True,
        index=True,
        primary_key=True,
        nullable=False
    )
    name: Mapped[str] = mapped_column(
        String(),
        nullable=False
    )
    username: Mapped[str] = mapped_column(
        String(),
        nullable=False
    )
    password: Mapped[str] = mapped_column(
        String(),
        nullable=False
    )
    registered_T: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP,
        default=datetime.datetime.utcnow(),
        nullable=False
    )
    role_id: Mapped[int] = mapped_column(
        Integer(),
        ForeignKey(role.c.id),
        nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(length=320),
        unique=True,
        index=True,
        nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(length=1024),
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )


engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
