from datetime import date
from pydantic import ValidationError

from app.auth.schemas import UserRead, UserCreate


def test_user_read_schema():
    user_data = {
        "id": 1,
        "name": "test",
        "email": "test@test",
        "username": "test",
        "role_id": 2,
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
    }

    user = UserRead(**user_data)

    assert user.id == 1
    assert user.name == "test"
    assert user.email == "test@test"
    assert user.username == "test"
    assert user.role_id == 2
    assert user.is_active == True
    assert user.is_superuser == False
    assert user.is_verified == False


def test_user_create_schema():
    user_data = {
        "name": "test",
        "email": "test@test",
        "username": "test",
        "password": "test",
        "role_id": 2,
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
        "register_timestamp": date.today(),
    }

    user = UserCreate(**user_data)

    assert user.name == "test"
    assert user.email == "test@test"
    assert user.username == "test"
    assert user.password == "test"
    assert user.role_id == 2
    assert user.is_active == True
    assert user.is_superuser == False
    assert user.is_verified == False
    assert user.register_timestamp == date.today()


def test_user_create_schema_invalid():
    invalid_user_data = {
        "name": "John Doe",
        "email": "invalid_email",
        "username": "john_doe",
        "password": "password123",
        "role_id": 2,
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
        "register_timestamp": date.today(),
    }

    try:
        user = UserCreate(**invalid_user_data)
    except ValidationError as e:
        assert "value is not a valid email address" in str(e)
