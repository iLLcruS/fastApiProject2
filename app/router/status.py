

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select, update, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.database_con import get_async_session
from app.core.custom_routers_func import query_execute
from app.models.tasks import task
from app.models.status import status as status_table


router = APIRouter(

    prefix="/task/status",
    tags=["task/status"],
)

class Status(BaseModel):
    status: str


@router.post("/create/")
async def create_status(status_name: str,
                        session: AsyncSession = Depends(get_async_session)):
    query = insert(status_table).values(name=status_name)
    await query_execute(query, session)
    return "Successfully created status!"


@router.post("/set/task/")
async def set_status(status_id: int,
                     task_id: int,
                     session: AsyncSession = Depends(get_async_session)):
    query = update(task).where(task.c.id == task_id).values(status_id=status_id)
    await query_execute(query, session)
    return "Successfully set status!"


@router.get("/get/all")
async def get_all_status(session: AsyncSession = Depends(get_async_session)):
    async with session as async_session:
        result = await async_session.execute(select(status_table))
        status = result.fetchall()
        print(task)

    statuses_data = [
        {
            "id": status_data.id,
            "name":status_data.name
        }
        for status_data in status
    ]

    return statuses_data



@router.delete("/delete/")
async def delete_status(status_id: int,
                        session: AsyncSession = Depends(get_async_session)):
    query = delete(status_table).where(status_table.c.id == status_id)
    await query_execute(query, session)
    return "Successfully deleted status!"


@router.post("/update/")
async def update_status(status_id: int,
                        new_name: str,
                        session: AsyncSession = Depends(get_async_session)):
    unbind = update(task).where(task.c.status_id == status_id).values(status_id=None)
    await query_execute(unbind, session)
    query = update(status_table).where(status_table.c.id == status_id).values(name=new_name)
    await query_execute(query, session)
    return "Successfully updated status!"


@router.get("/get/by_name")
async def get_status(status_name: str,
                     session: AsyncSession = Depends(get_async_session)):
    query = select(status_table).where(status_table.c.name == status_name)
    result = await query_execute(query, session)
    status = result.fetchone()

    return {"id": status[0], "name": status[1]}


@router.get("/get")
async def get_statuses(session: AsyncSession = Depends(get_async_session)):

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
