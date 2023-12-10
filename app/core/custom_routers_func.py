from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.logger import logger
from config import SECRET_KEY_JWT
from fastapi import Request
import jwt

def decode_user(token: str):
    """
    :param token: jwt token
    :return:
    """
    decoded_data = jwt.decode(jwt=token,
                              key=f'{SECRET_KEY_JWT}',
                              algorithms=["HS256"],
                              audience="fastapi-users:auth"
                              )
    return decoded_data


def get_user_id_from_token(request: Request) -> int:
    cookie = request.cookies.get("trello")
    user_data = decode_user(cookie)
    return int(user_data['sub'])


async def query_execute(query, session: AsyncSession):
    result = await session.execute(query)
    await session.commit()
    await session.close()
    return result


async def log_operation(session: AsyncSession, subject: str, user_id: int, email: str):
    log_data = {
        "log_subject": subject,
        "log_id_user": user_id,
        "log_email_user": email,
    }
    log_query = insert(logger).values(log_data)
    await session.execute(log_query)
    await session.commit()