from sqlalchemy import MetaData, Table, Column, Integer, String

metadata = MetaData()

status = Table(
    "status",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False)
)