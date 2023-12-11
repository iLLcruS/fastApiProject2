from sqlalchemy import insert, update, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.tasks import task as task_table
from app.auth.database_con import get_async_session
from app.models.board import board as board_table
from app.core.custom_routers_func import query_execute
from fastapi import APIRouter, Request, Depends

router = APIRouter(

    prefix="/board/{user_name}",
    tags=["board"],
)


@router.post("/create/{board_title}")
async def create_board(request: Request,
                       board_title: str,
                       user_name: str,
                       session: AsyncSession = Depends(get_async_session)):
    query = insert(board_table).values(title=board_title)
    await query_execute(query, session)
    return "Board successfully created!"


@router.post("/{board_id}/set/task/{task_id}/")
async def set_board_to_task(request: Request,
                            task_id: int,
                            board_id: int,
                            user_name: str,
                            session: AsyncSession = Depends(get_async_session)):
    query = update(task_table).where(task_table.c.id == task_id).values(board_id=board_id)
    await query_execute(query, session)
    return "Task board, successfully updated!"


@router.delete("/delete/{board_id}")
async def delete_board(request: Request,
                       board_id: int,
                       user_name: str,
                       session: AsyncSession = Depends(get_async_session)):
    query = update(task_table).where(task_table.c.board_id == board_id).values(board_id=None)
    await query_execute(query, session)
    query = delete(board_table).where(board_table.c.id == board_id)
    await query_execute(query, session)
    return "Board, successfully deleted!"


@router.get("/all")
async def get_all_boards(request: Request,
                         user_name: str,
                         session: AsyncSession = Depends(get_async_session)):
    query = select(board_table)
    result = await query_execute(query, session)
    statuses_raw = result.fetchall()
    statuses = []
    for tup in statuses_raw:
        status_data = {
            "id": tup[0],
            "title": tup[1]
        }
        statuses.append(status_data)
    return statuses


@router.get("/get/title/{title}")
async def get_by_title(request: Request,
                       user_name: str,
                       title: str,
                       session: AsyncSession = Depends(get_async_session)):
    query = select(board_table).where(board_table.c.title == title)
    result = await query_execute(query, session)
    board = result.fetchone()
    if board is None:
        return "404 not found!"
    return {"id": board[0], "title": board[1]}


@router.post("/update/{board_id}/title/{title}")
async def update_board(request: Request,
                       user_name: str,
                       title: str,
                       board_id: int,
                       session: AsyncSession = Depends(get_async_session)):
    query = update(board_table).where(board_table.c.id == board_id).values(title=title)
    await query_execute(query, session)
    return "'status code 200' if 'All ok!' else '500 internal server error!'"
