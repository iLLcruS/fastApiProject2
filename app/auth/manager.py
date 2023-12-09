from typing import Optional

from fastapi import Depends, Request
from fastapi_mail import FastMail, MessageSchema
from fastapi_users import BaseUserManager, IntegerIDMixin, exceptions, models, schemas
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.logger import logger
from config import SECRET_KEY_JWT_VERIFICATION_RESET
from app.auth.database_con import User, get_user_db, engine

SECRET = f"{SECRET_KEY_JWT_VERIFICATION_RESET}"


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):

        async with AsyncSession(engine) as session:
            try:
                await log_operation(session, 'Registered', user.id, user.email)
            except Exception as e:
                await log_operation(session, f"Registered Failed: {str(e)}", user.id, user.email)
        print(f"User {user.id} has registered.")

    async def create(
            self,
            user_create: schemas.UC,
            safe: bool = False,
            request: Optional[Request] = None,
    ) -> models.UP:

        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)
        user_dict["role_id"] = 1

        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user, request)

        return created_user


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


async def log_operation(session: AsyncSession, subject: str, user_id: int, email: str):
    log_data = {
        "log_subject": subject,
        "log_id_user": user_id,
        "log_email_user": email,
    }
    log_query = insert(logger).values(log_data)
    await session.execute(log_query)
    await session.commit()