
from fastapi import FastAPI
from fastapi_users import FastAPIUsers
from fastapi.responses import RedirectResponse
from starlette.staticfiles import StaticFiles

from .auth.auth import auth_backend
from .auth.database_con import User, engine
from .auth.manager import get_user_manager
from .auth.schemas import UserRead, UserCreate
from .router.tasks import router as task_router
from .router.admin import router_admin as admin_router
from .router.board import router as board_router
from .router.sendmail import router as mail_router

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

app = FastAPI(
    title="Trello(demo)"
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def main_page():
    redirect_url = "/docs"

    response = RedirectResponse(url=redirect_url)
    return response


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
    status_router
)
app.include_router(
    board_router
)
app.include_router(
    mail_router
)


