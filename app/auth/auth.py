from fastapi_users.authentication import CookieTransport, AuthenticationBackend
from fastapi_users.authentication import JWTStrategy
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.logger import logger
from app.auth.database_con import engine
from app.config import SECRET_KEY_JWT

cookie_transport = CookieTransport(cookie_name="trello", cookie_max_age=3600)

SECRET = f"{SECRET_KEY_JWT}"


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


async def log_operation(subject: str, user_id: int, email: str):
    async with AsyncSession(engine) as session:
        log_data = {
            "log_subject": subject,
            "log_id_user": user_id,
            "log_email_user": email,
        }
        log_query = insert(logger).values(log_data)
        await session.execute(log_query)
        await session.commit()


class CustomAuthBackend(AuthenticationBackend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def login(self, strategy, user):
        try:
            await log_operation(subject="Login", user_id=user.id, email=user.email)
        except Exception as e:
            print(f"Error during login log operation: {e}")
        return await super().login(strategy, user)

    async def logout(self, strategy, user, token):
        try:
            await log_operation(subject="Login", user_id=user.id, email=user.email)
        except Exception as e:
            print(f"Error during logout log operation: {e}")
        return await super().logout(strategy, user, token)


auth_backend = CustomAuthBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)
