from sqlalchemy import insert, update, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.tasks import task as task_table
from app.auth.database_con import get_async_session
from app.models.board import board as board_table
from app.core.custom_routers_func import query_execute
from fastapi import APIRouter, Request, Depends
from app.core.custom_routers_func import get_user_id_from_token

router = APIRouter(

    prefix="/board",
    tags=["board"],
)


@router.post("/create/{board_title}")
async def create_board(request: Request,
                       board_title: str,
                       session: AsyncSession = Depends(get_async_session)):
    query = insert(board_table).values(title=board_title)
    user_id = get_user_id_from_token(request)
    await query_execute(query, session)

    query = select(task_table).where(task_table.c.title == board_title)
    result = await query_execute(query, session)

    return "Board successfully created!"


@router.post("/{board_id}/set/task/{task_id}/")
async def set_board_to_task(request: Request,
                            task_id: int,
                            board_id: int,
                            session: AsyncSession = Depends(get_async_session)):
    query = update(task_table).where(task_table.c.id == task_id).values(board_id=board_id)
    await query_execute(query, session)
    return "Task board, successfully updated!"


@router.delete("/delete/{board_id}")
async def delete_board(request: Request,
                       board_id: int,
                       session: AsyncSession = Depends(get_async_session)):
    query = update(task_table).where(task_table.c.board_id == board_id).values(board_id=None)
    await query_execute(query, session)
    query = delete(board_table).where(board_table.c.id == board_id)
    await query_execute(query, session)
    return "Board, successfully deleted!"


@router.get("/all")
async def get_all_boards(request: Request,
                         session: AsyncSession = Depends(get_async_session)):
    user_id = get_user_id_from_token(request)
    query = select(board_table)
    result = await query_execute(query, session)
    statuses_raw = result.fetchall()
    statuses = []
    for tup in statuses_raw:
        status_data = {
            "id": tup[0],
            "title": tup[1]
        }

        if user_id in tup[0]:
            statuses.append(status_data)
    return statuses


@router.get("/get/title/{title}")
async def get_by_title(request: Request,
                       title: str,
                       session: AsyncSession = Depends(get_async_session)):
    user_id = get_user_id_from_token(request)
    query = select(board_table).where(board_table.c.title == title)
    result = await query_execute(query, session)
    board = result.fetchone()
    if board is None:
        return "404 not found!"
    if user_id == board[0]:
        return {"id": board[0], "title": board[1]}
    else:
        return "404 Not found!"


@router.post("/update/{board_id}/title/{title}")
async def update_board(request: Request,
                       title: str,
                       board_id: int,
                       session: AsyncSession = Depends(get_async_session)):
    query = update(board_table).where(board_table.c.id == board_id).values(title=title)
    await query_execute(query, session)
    return "'status code 200' if 'All ok!' else '500 internal server error!'"


async def add_to_allowed_users(session: AsyncSession, board_id: int, user_id: int):
    query = select(board_table).where(board_table.c.id == board_id)
    result = await query_execute(query, session)

    list_allowed_users: list = result.fetchone()[9]
    print(list_allowed_users)
    list_allowed_users.append(user_id)
    query = update(board_table).where(board_table.c.id == board_id).values(
        allowed_user_ids=list_allowed_users)
    await query_execute(query, session)


async def get_allowed_user_id(session: AsyncSession, board_id: int, user_id: int):
    query = select(board_table).where(board_table.c.id == board_id)
    result = await query_execute(query, session)
    list_allowed_users: list = result.fetchone()[9]
    return list_allowed_users


async def remove_from_allowed_users(session: AsyncSession, task_id: int, user_id: int):
    query = select(board_table).where(board_table.c.id == task_id)
    result = await query_execute(query, session)

    list_allowed_users: list = result.fetchone()[9]
    print(list_allowed_users)
    try:
        list_allowed_users.remove(user_id)
    except Exception as e:
        ...
    query = update(board_table).where(board_table.c.id == task_id).values(
        allowed_user_ids=list_allowed_users)
    await query_execute(query, session)


@router.post("/add/{board_id}/user/{user_id}")
async def add_user_to_board(request: Request,
                            user_id: int,
                            board_id: int,
                            session: AsyncSession = Depends(get_async_session)):
    await add_to_allowed_users(session, board_id, user_id)
    return "All ok!"


@router.post("/add/{board_id}/user/{user_id}")
async def remove_user_from_board(request: Request,
                                 user_id: int,
                                 board_id: int,
                                 session: AsyncSession = Depends(get_async_session)):
    await remove_from_allowed_users(session, board_id, user_id)
    return "All ok!"
