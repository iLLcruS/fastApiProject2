from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from pydantic import BaseModel
from sqlalchemy import select, update, insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.custom_routers_func import log_operation
from app.auth.database_con import get_user_db, get_async_session, engine
from app.models.logger import logger
from app.models.user import user as User, role
from app.router.tasks import get_user_id_from_token, query_execute

router_admin = APIRouter(
    prefix="/admin",
    tags=["admin"],
)


class UpdateUserRoleData(BaseModel):
    role_id: int


class UpdateUserEmailData(BaseModel):
    email: str


class UpdateRoleData(BaseModel):
    id: int
    name_role: str

async def get_current_user_role(request: Request, user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    current_user = await user_db.get(get_user_id_from_token(request))
    if current_user.role_id != 2:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    return current_user.role_id


@router_admin.get("/log")
async def get_logs_route(
        current_user_role: int = Depends(get_current_user_role),
        session: AsyncSession = Depends(get_async_session)
):
    try:
        query = select(logger.c.log_id, logger.c.log_subject, logger.c.log_id_user, logger.c.log_email_user,
                       logger.c.log_time)
        result = await session.execute(query)
        logs = result.fetchall()

        logs_data = [
            {
                "log_id": log.log_id,
                "log_subject": log.log_subject,
                "log_id_user": log.log_id_user,
                "log_email_user": log.log_email_user,
                "log_time": log.log_time,
            }
            for log in logs
        ]

        return {"logs": logs_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router_admin.post("/update/role")
async def update_user_role_id(update_data: UpdateUserRoleData,
                              user_name: str,
                              request: Request,
                              user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
                              ):
    user_id = get_user_id_from_token(request)
    user_email = await user_db.get(user_id)

    user_update_data = {"role_id": update_data.role_id}

    user_update_condition = User.c.username == user_name

    query = update(User).values(user_update_data).where(user_update_condition)

    async with AsyncSession(engine) as session:
        try:
            await query_execute(query, session)
            await log_operation(session, "Updated User Role", user_id, f'{user_email.email}')
            return f'User {user_name} role was updated to {update_data.role_id}'
        except Exception as e:
            await log_operation(session, f"User Role Update Failed: {str(e)}", user_id, f'{user_email.email}')
            return "Error during user role update"


@router_admin.post("/add/role")
async def create_role(request: Request, role_data: UpdateRoleData,
                      user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):

    query = insert(role).values(
        id=role_data.id,
        name_role=role_data.name_role
    )
    success_message = "Role Add"

    async with AsyncSession(engine) as session:
        try:
            await query_execute(query, session)
            return f'{success_message}'
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
