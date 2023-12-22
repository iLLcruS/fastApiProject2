from typing import List

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from pydantic import BaseModel
from sqlalchemy import select, update, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.database_con import get_user_db, get_async_session, engine, User
from app.core.custom_routers_func import get_user_id_from_token, query_execute, execute_task_operation, log_operation, \
    add_to_allowed_users, remove_from_allowed_users
from app.models.tasks import task

router = APIRouter(

    prefix="/task",
    tags=["tasks"],
)


class Task(BaseModel):
    title: str
    description: str
    keywords: List[str] = []
    user_executor_id: int


class UpdateTask(BaseModel):
    title: str
    description: str
    user_executor_id: int


class TaskDeleteData(BaseModel):
    task_id: int


async def get_current_user(request: Request, session: AsyncSession = Depends(get_async_session)) -> User:
    user_id = get_user_id_from_token(request)
    async with session as async_session:
        result = await async_session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        return user


@router.post("/add")
async def create_task(request: Request, task_data: Task,
                      user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    user_id = get_user_id_from_token(request)
    user_email = await user_db.get(user_id)

    subtasks = []

    if task_data.keywords:
        for keyword in task_data.keywords:
            if keyword.lower() in task_data.description.lower():
                subtasks.append((f"{keyword.capitalize()} Task", f"Description for {keyword.capitalize()} Task"))

    query = insert(task).values(
        title=task_data.title,
        description=task_data.description,
        user_executor_id=task_data.user_executor_id,
        user_creator_id=user_id,
        allowed_to_visible_user_ids=[user_id],
        keywords=task_data.keywords,
    )

    async with AsyncSession(engine) as session:
        try:
            result = await query_execute(query, session)
            await log_operation(session, "Task Created", user_id, f'{user_email.email}')
            task_id = result.fetchone()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")

    for subtask_title, subtask_description in subtasks:
        subtask_query = insert(task).values(
            title=subtask_title,
            description=subtask_description,
            user_creator_id=user_id,
            user_executor_id=task_data.user_executor_id,
            parent_task_id=task_id,
            allowed_to_visible_user_ids=[user_id],
        )
        async with AsyncSession(engine) as session:
            try:
                await query_execute(subtask_query, session)
                await log_operation(session, "Task Created", user_id, f'{user_email.email}')
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")

    return f': Создана задача: {task_id}'


@router.post("/edit")
async def update_task(request: Request, task_id: int, task_data: UpdateTask,
                      user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    user_id = get_user_id_from_token(request)

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


@router.delete("/erase")
async def erase_task(request: Request, task_id: str,
                     user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    user_id = get_user_id_from_token(request)

    if id is not None:
        query = delete(task).where(task.c.id == int(task_id))
        success_message = "Deleted Task"

        return await execute_task_operation(request, user_id, query, success_message, user_db)


@router.get("/get/all")
async def get_all_tasks(session: AsyncSession = Depends(get_async_session)):
    async with session as async_session:
        result = await async_session.execute(select(task))
        tasks = result.fetchall()
        print(task)

    tasks_data = [
        {
            "id": task_data.id,
            "title": task_data.title,
            "description": task_data.description,
            "user_executor_id": task_data.user_executor_id,
            "user_creator_id": task_data.user_creator_id,
            "status_id": task_data.status_id
        }
        for task_data in tasks
    ]

    return tasks_data


@router.get("/task/add/user/")
async def add_user_to_visible(request: Request,
                              user_id: int,
                              task_id: int,
                              session: AsyncSession = Depends(get_async_session)):
    await add_to_allowed_users(session, task_id, user_id)
    return "User was add"


@router.get("/task/remove/user/")
async def remove_user_from_visible(request: Request,
                                   user_id: int,
                                   task_id: int,
                                   session: AsyncSession = Depends(get_async_session)):
    await remove_from_allowed_users(session, task_id, user_id)
    return "User was delete"
