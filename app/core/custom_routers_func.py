from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.database_con import get_user_db, engine
from app.models.logger import logger
from app.config import SECRET_KEY_JWT
from fastapi import Request, HTTPException, Depends
import jwt

from app.models.tasks import task


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


async def execute_task_operation(request: Request, user_id: int, query, success_message,
                                 user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    user_email = await user_db.get(user_id)

    async with AsyncSession(engine) as session:
        try:
            await query_execute(query, session)
            await log_operation(session, success_message, user_id, f'{user_email.email}')
            return f'{success_message}: {user_id}'
        except Exception as e:
            await log_operation(session, f"{success_message} Failed: {str(e)}", user_id, f'{user_email.email}')
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


async def add_to_allowed_users(session: AsyncSession, task_id: int, user_id: int):
    query = select(task).where(task.c.id == task_id)
    result = await query_execute(query, session)

    list_allowed_users: list = result.fetchone()[9]
    print(list_allowed_users)
    list_allowed_users.append(user_id)
    query = update(task).where(task.c.id == task_id).values(allowed_to_visible_user_ids=list_allowed_users)
    await query_execute(query, session)


async def get_allowed_user_id(session: AsyncSession, task_id: int):
    query = select(task).where(task.c.id == task_id)
    result = await query_execute(query, session)
    list_allowed_users: list = result.fetchone()[9]
    return list_allowed_users


async def remove_from_allowed_users(session: AsyncSession, task_id: int, user_id: int):
    query = select(task).where(task.c.id == task_id)
    result = await query_execute(query, session)

    list_allowed_users: list = result.fetchone()[9]
    print(list_allowed_users)
    try:
        list_allowed_users.remove(user_id)
    except Exception as e:
        ...
    query = update(task).where(task.c.id == task_id).values(allowed_to_visible_user_ids=list_allowed_users)
    await query_execute(query, session)

