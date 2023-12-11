import jwt
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from pydantic import BaseModel
from sqlalchemy import select, update, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.database_con import get_user_db, get_async_session, engine
from app.core.custom_routers_func import get_user_id_from_token, query_execute, execute_task_operation
from app.models.tasks import task
from app.models.status import status as status_table
from config import SECRET_KEY_JWT

router = APIRouter(

    prefix="/task",
    tags=["tasks"],
)


class Task(BaseModel):
    title: str
    description: str
    user_executor_id: int
    status_id: int


class UpdateTask(BaseModel):
    title: str
    description: str
    user_executor_id: int


class TaskDeleteData(BaseModel):
    task_id: int


@router.get("")
async def redirect_to_current_user_tasks(request: Request, user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    user_id = await get_user_id_from_token(request)
    user = await user_db.get(user_id)
    redirect_url = f'/task/{user.username}'
    return RedirectResponse(redirect_url)


@router.post("/{user_name}/add")
async def create_task(request: Request, user_name: str, task_data: Task,
                      user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    user_id = get_user_id_from_token(request)

    query = insert(task).values(
        title=task_data.title,
        description=task_data.description,
        user_executor_id=task_data.user_executor_id,
        user_creator_id=user_id,
        status_id=task_data.status_id,
        allowed_to_visible_user_ids = [user_id]
    )

    success_message = "Created Task"
    return await execute_task_operation(request, user_id, query, success_message, user_db)


@router.post("/{username}/edit/{task_id}")
async def update_task(request: Request, user_name: str, task_id: int, task_data: UpdateTask,
                      user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    user_id = get_user_id_from_token(request)
    user_email = await user_db.get(user_id)

    task_update_data = {
        "title": task_data.title,
        "description": task_data.description,
        "user_executor_id": task_data.user_executor_id,
        "user_creator_id": user_id,
    }
    task_update_condition = task.c.id == int(task_id)

    query = update(task).values(task_update_data).where(task_update_condition)
    success_message = "Updated Task"

    return await execute_task_operation(request, user_id, query, success_message, user_db)


@router.delete("/{user_name}/erase/{task_id}")
async def erase_task(request: Request, user_name: str, task_id: str,
                     session: AsyncSession = Depends(get_async_session),
                     user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    user_id = get_user_id_from_token(request)
    user_email = await user_db.get(user_id)

    if id is not None:
        query = delete(task).where(task.c.id == int(task_id))
        success_message = "Deleted Task"

        return await execute_task_operation(request, user_id, query, success_message, user_db)


@router.get("/get")
async def get_tasks(task_title: str, session: AsyncSession = Depends(get_async_session)):
    query = select(task).where(task.c.title == task_title)
    result = await session.execute(query)
    await session.close()
    return result.all()


class Status(BaseModel):
    status: str


@router.post("/{user_name}/status/create/{status_name}")
async def create_status(request: Request,
                        status_name: str,
                        user_name: str,
                        session: AsyncSession = Depends(get_async_session)):
    query = insert(status_table).values(name=status_name)
    await query_execute(query, session)
    return "Successfully created status!"


@router.post("/{user_name}/status/set/{status_id}/task/{task_id}")
async def set_status(request: Request,
                     status_id: int,
                     user_name: str,
                     task_id: int,
                     session: AsyncSession = Depends(get_async_session)):
    query = update(task).where(task.c.id == task_id).values(status_id=status_id)
    await query_execute(query, session)
    return "Successfully set status!"


@router.delete("/{user_name}/status/delete/{status_id}")
async def delete_status(request: Request,
                        status_id: int,
                        user_name: str,
                        session: AsyncSession = Depends(get_async_session)):
    query = delete(status_table).where(status_table.c.id == status_id)
    await query_execute(query, session)
    return "Successfully deleted status!"


@router.post("/{user_name}/status/update/{status_id}")
async def update_status(request: Request,
                        status_id: int,
                        user_name: str,
                        new_name: str,
                        session: AsyncSession = Depends(get_async_session)):
    unbind = update(task).where(task.c.status_id == status_id).values(status_id=None)
    await query_execute(unbind, session)
    query = update(status_table).where(status_table.c.id == status_id).values(name=new_name)
    await query_execute(query, session)
    return "Successfully updated status!"


@router.get("/{user_name}/status/get/{status_name}")
async def get_status(request: Request,
                     user_name: str,
                     status_name: str,
                     session: AsyncSession = Depends(get_async_session)):
    query = select(status_table).where(status_table.c.name == status_name)
    result = await query_execute(query, session)
    status = result.fetchone()

    return {"id": status[0], "name": status[1]}


@router.get("/{user_name}/statuses/get")
async def get_statuses(request: Request,
                       user_name: str,
                       session: AsyncSession = Depends(get_async_session)):
    query = select(status_table)
    result = await query_execute(query, session)
    statuses_raw = result.fetchall()
    statuses = []
    for tup in statuses_raw:
        status_data = {
            "id": tup[0],
            "name": tup[1]
        }
        statuses.append(status_data)
    return statuses
