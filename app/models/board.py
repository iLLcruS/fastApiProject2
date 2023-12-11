from sqlalchemy import MetaData, Table, Column, Integer, String, ARRAY

metadata = MetaData()

board = Table(
    "board",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String, nullable=False),
    Column("allowed_user_ids", ARRAY(Integer))
)