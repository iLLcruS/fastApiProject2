import datetime as dt
from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, JSON, Boolean, TIMESTAMP, func, DateTime

from app.models.user import user

metadata = MetaData()

board = Table(
    "board",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String, nullable=False)
)