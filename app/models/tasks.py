import datetime as dt
from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, JSON, Boolean, TIMESTAMP, func, DateTime, \
    ARRAY, Text, LargeBinary

from app.models.status import status
from app.models.user import user
from app.models.board import board as board_table


metadata = MetaData()

task = Table(
    "task",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String, nullable=False),
    Column("description", String, nullable=True),
    Column("start_timestamp", DateTime(timezone=True), server_default=func.now(), default=dt.datetime.now().date(), nullable=False),
    Column("user_creator_id", Integer, ForeignKey(user.c.id)),
    Column("user_executor_id", Integer, ForeignKey(user.c.id)),
    Column("status_id", Integer, ForeignKey(status.c.id), nullable=True),
    Column("board_id", Integer, ForeignKey(board_table.c.id)),
    Column("parent_task_id", Integer, ForeignKey("task.id"), nullable=True),
    Column("allowed_to_visible_user_ids", ARRAY(Integer)),
    Column("text_content", Text, nullable=True),
    Column("image_url", String, nullable=True),
    Column("video_url", String, nullable=True),
    Column("audio_url", String, nullable=True),
    Column("image_content", LargeBinary, nullable=True),
)
