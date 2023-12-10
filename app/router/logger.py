from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.database_con import get_user_db, get_async_session
from app.models.logger import logger
from app.router.tasks import get_user_id_from_token

router_admin = APIRouter(
    prefix="/admin",
    tags=["router"],
)


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