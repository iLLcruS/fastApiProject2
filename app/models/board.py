import datetime as dt
from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, JSON, Boolean, TIMESTAMP, func, DateTime, \
    ARRAY

from app.models.user import user

metadata = MetaData()

board = Table(
    "board",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String, nullable=False),
    Column("allowed_user_ids", ARRAY(Integer))
)