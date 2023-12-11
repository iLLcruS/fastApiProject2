from typing import Optional

from fastapi import Depends, Request
from fastapi_mail import FastMail, MessageType, ConnectionConfig, MessageSchema
from fastapi_users import BaseUserManager, IntegerIDMixin, exceptions, models, schemas
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.custom_routers_func import log_operation
from config import SECRET_KEY_JWT_VERIFICATION_RESET
from app.auth.database_con import User, get_user_db, engine

SECRET = f"{SECRET_KEY_JWT_VERIFICATION_RESET}"


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def send_registration_notification(self, user: User):

        message = MessageSchema(
            subject="Registration Notification",
            recipients=[user.email],
            body=f"Dear {user.email},\n\nThank you for registering with us!\n\nBest regards,\nTrello",
            subtype=MessageType.plain
        )
        await self.send_email(message)

    async def on_after_register(self, user: User, request: Optional[Request] = None):

        async with AsyncSession(engine) as session:
            try:
                await log_operation(session, 'Registered', user.id, user.email)
            except Exception as e:
                await log_operation(session, f"Registered Failed: {str(e)}", user.id, user.email)
        print(f"User {user.id} has registered.")

        await self.send_registration_notification(user)

    async def send_email(message: MessageSchema):
        connection_config = ConnectionConfig(
            MAIL_USERNAME="rostovskii.1020@gmail.com",
            MAIL_PASSWORD="orrd qjam nnjm cvjs",
            MAIL_FROM="rostovskii.1020@gmail.com",
            MAIL_PORT=587,
            MAIL_SERVER="smtp.gmail.com",
            MAIL_SSL_TLS=False,
            MAIL_STARTTLS=True,
            USE_CREDENTIALS=True,
            MAIL_DEBUG=0,
            MAIL_FROM_NAME="Trello",
            SUPPRESS_SEND=0,
            VALIDATE_CERTS=False,
            TIMEOUT=30,
        )
        fm = FastMail(connection_config)
        await fm.send_message(message)

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
