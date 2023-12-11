
from fastapi import FastAPI
from fastapi_users import fastapi_users, FastAPIUsers

from app.auth.auth import auth_backend
from app.auth.database_con import User
from app.auth.manager import get_user_manager
from app.auth.schemas import UserRead, UserCreate
from app.router.tasks import router as task_router
from app.router.admin import router_admin as admin_router
from app.router.board import router as board_router
from app.router.sendmail import router as mail_router


fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

app = FastAPI(
    title="Trello(demo)"
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    task_router
)

app.include_router(
    admin_router
)
app.include_router(
    board_router
)
app.include_router(
    mail_router
)


