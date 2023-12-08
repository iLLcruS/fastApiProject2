import datetime

from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    id: int
    name: str
    email: str
    username: str
    role_id: int
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False


class UserCreate(schemas.BaseUserCreate):
    name: str
    email: str
    username: str
    password: str
    role_id: int
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
