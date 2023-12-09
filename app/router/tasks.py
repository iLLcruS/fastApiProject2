import datetime
from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse
from sqlalchemy import select, update
from app.auth.database_con import get_user_db, get_async_session
import jwt
from app.auth.database_con import engine
from app.models.tasks import task
from sqlalchemy import insert, delete

from config import SECRET_KEY_JWT

router = APIRouter(

    prefix="/task",
    tags=["router"],
)


def decode_user(token: str):
    """
    :param token: jwt token
    :return:
    """
    decoded_data = jwt.decode(jwt=token,
                              key=f'{SECRET_KEY_JWT}',
                              algorithms=["HS256"],
                              audience="Trello Auth"
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


@router.get("")
async def redirect_to_current_user_tasks(request: Request, user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    user_id = await get_user_id_from_token(request)
    user = await user_db.get(user_id)
    redirect_url = f'/task/{user.username}'
    return RedirectResponse(redirect_url)


class Task(BaseModel):
    title: str
    description: str
    user_executor_id: int
    end_timestamp: datetime.datetime


class UpdateTask(BaseModel):
    title: str
    description: str
    user_executor_id: int
    end_timestamp: datetime.datetime


class TaskDeleteData(BaseModel):
    task_id: int


@router.post("/{user_name}/add")
async def create_task(request: Request, user_name: str, task_data: Task,
                      user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    user_id = get_user_id_from_token(request)
    query = insert(task).values(
        title=task_data.title,
        description=task_data.description,
        user_executor_id=task_data.user_executor_id,
        end_timestamp=task_data.end_timestamp,
        user_creator_id=user_id
    )
    async with AsyncSession(engine) as session:
        await query_execute(query, session)
    return "ALL OK~!"


@router.post("/{username}/edit/{task_id}")
async def update_task(request: Request, user_name: str, task_id: int, task_data: UpdateTask,
                      user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    user_id = get_user_id_from_token(request)

    task_update_data = {
        "title": task_data.title,
        "description": task_data.description,
        "user_executor_id": task_data.user_executor_id,
        "end_timestamp": task_data.end_timestamp,
        "user_creator_id": user_id,
    }

    task_update_condition = task.c.id == int(task_id)

    query = update(task).values(task_update_data).where(task_update_condition)

    async with AsyncSession(engine) as session:
        await query_execute(query, session)
    return "Date updated"


@router.delete("/{user_name}/erase/{task_id}")
async def erase_task(request: Request, user_name: str,task_id: str,
                     session: AsyncSession = Depends(get_async_session)):
    if id is not None:
        query = delete(task).where(task.c.id == int(task_id))
        await query_execute(query, session)
        return f'Successfully deleted task with id - {task_id}'
    else:
        return {"message": "Error: value title or id must be not empty"}


@router.get("/get")
async def get_tasks(task_title: str, session: AsyncSession = Depends(get_async_session)):
    query = select(task).where(task.c.title == task_title)
    result = await session.execute(query)
    await session.close()
    return result.fetchall()

class Status(BaseModel):
    status: str

@router.post("/{username}/set/status/{}")
async def set_status(request: Request, user_name: str,task_id: int,
                     status = Status,
                     session: AsyncSession = Depends(get_async_session)):
    query = update(task).where(task.c.id == int(task_id)).values()
