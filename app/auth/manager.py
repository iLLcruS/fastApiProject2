from typing import Optional

from fastapi import Depends, Request
from fastapi_mail import FastMail, MessageSchema
from fastapi_users import BaseUserManager, IntegerIDMixin, exceptions, models, schemas

from config import SECRET_KEY_JWT_VERIFICATION_RESET
from .database_con import User, get_user_db

SECRET = f"{SECRET_KEY_JWT_VERIFICATION_RESET}"

mail_config = {
}

mail = FastMail(mail_config)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        subject = "Thank you for registration! "
        body = f"Your account was registered, welcome, {user.name}!"

        message = MessageSchema(
            subject=subject,
            recipients=[user.email],
            body=body,
            subtype="html"
        )

        try:
            await mail.send_message(message)
            print(f"Email sent to {user.email} for user {user.id} registration.")
        except Exception as e:
            print(f"Failed to send email. Error: {str(e)}")
        print(f"User {user.id} has registered. Email was sent")

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