import datetime as dt
from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, JSON, Boolean, TIMESTAMP, func, DateTime

from app.models.status import status
from app.models.user import user


metadata = MetaData()

task = Table(
    "task",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String, nullable=False),
    Column("description", String, nullable=True),
    Column("start_timestamp", TIMESTAMP, arbitrary_types_allowed=True, nullable=False),
    Column("user_creator_id", Integer, ForeignKey(user.c.id)),
    Column("user_executor_id", Integer, ForeignKey(user.c.id)),
    Column("status_id", Integer, ForeignKey(status.c.id), nullable=True)
)
