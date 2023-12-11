from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from config import DB_USER, DB_PASS, DB_HOST, DB_NAME, DB_PORT, MAIL_NAME, MAIL_PASSWORD
from app.models.user import metadata as metadata_user
from app.models.tasks import metadata as metadata_tasks
from app.models.logger import metadata as metadata_logger
from app.models.status import metadata as metadata_status
from app.models.board import metadata as metadata_board

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

section = config.config_ini_section
config.set_section_option(section, "DB_USER", DB_USER)
config.set_section_option(section, "DB_PASS", DB_PASS)
config.set_section_option(section, "DB_HOST", DB_HOST)
config.set_section_option(section, "DB_NAME", DB_NAME)
config.set_section_option(section, "DB_PORT", DB_PORT)
config.set_section_option(section, "MAIL_NAME", MAIL_NAME)
config.set_section_option(section, "MAIL_PASSWORD", MAIL_PASSWORD)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = [metadata_user, metadata_board, metadata_status, metadata_tasks, metadata_logger]

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
