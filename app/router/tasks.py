import jwt
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from pydantic import BaseModel
from sqlalchemy import select, update, insert, delete, cast, ARRAY, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.database_con import get_user_db, get_async_session, engine
from app.core.custom_routers_func import get_user_id_from_token, query_execute, execute_task_operation
from app.models.tasks import task
from app.models.status import status as status_table
from sqlalchemy import or_, and_

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
        allowed_to_visible_user_ids=[user_id]
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


@router.get("/get/{task_title}")
async def get_task(request: Request,
                   task_title: str, session: AsyncSession = Depends(get_async_session)):
    try:
        user_id = get_user_id_from_token(request)
    except Exception as e:
        print(e)
        return "403 FORBIDDEN"

    query = select(task).where(or_(task.c.user_executor_id == user_id,
                                   task.c.user_creator_id == user_id,
                                   ))
    result_raw = await session.execute(query)
    result = result_raw.fetchone()
    await session.close()

    if result is None:
        return "404 Not found"

    response = []

    column_names = ["id", "title", "description", "start_timestamp",
                    "user_creator_id", "user_executor_id", "status_id",
                    "board_id", "parent_task_id"]

    if result is not None:
        data = {column_names[i]: result[i] for i in range(len(column_names))}

        user_ids = await get_allowed_user_id(session, data["id"])

        if user_id in user_ids:
            response.append(data)

    if result is None:
        return "404 Not found"
    return response


@router.get("/all")
async def get_tasks(request: Request,
                    session: AsyncSession = Depends(get_async_session)):
    try:
        user_id = get_user_id_from_token(request)
    except Exception as e:
        print(e)
        return "403 FORBIDDEN"

    query = select(task).where(or_(task.c.user_executor_id == user_id,
                                   task.c.user_creator_id == user_id,
                                   cast([await get_allowed_user_id(session, )], ARRAY(Integer)).overlap(
                                       task.c.allowed_to_visible_user_ids)))
    result_raw = await session.execute(query)
    result = result_raw.fetchall()
    await session.close()
    if result is None:
        return "404 Not found"
    response = []
    for tup in result:
        data = {}
        data["id"] = tup[0]
        data["title"] = tup[1]
        data["description"] = tup[2]
        data["start_timestamp"] = tup[3]
        data["user_creator_id"] = tup[4]
        data["user_executor_id"] = tup[5]
        data["status_id"] = tup[6]
        data["board_id"] = tup[7]
        data["parent_task_id"] = tup[8]

        user_ids = await get_allowed_user_id(session, data["id"])

        if user_id in user_ids:
            response.append(data)

        response.append(data)

    return response


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


@router.get("/{user_name}/task/{task_id}/add/user/{user_id}")
async def add_user_to_visible(request: Request,
                              user_name: str,
                              user_id: int,
                              task_id: int,
                              session: AsyncSession = Depends(get_async_session)):
    await add_to_allowed_users(session, task_id, user_id)
    return "All ok"


@router.get("/{user_name}/task/{task_id}/remove/user/{user_id}")
async def remove_user_from_visible(request: Request,
                                   user_name: str,
                                   user_id: int,
                                   task_id: int,
                                   session: AsyncSession = Depends(get_async_session)):
    await remove_from_allowed_users(session, task_id, user_id)
    return "All ok!"
