from alembic import context
from sqlalchemy import create_engine, pool

from app.core.config import Settings
from app.models import Family

target_metadata = Family.metadata


def configure(connection):
    context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    context.configure(
        url=Settings().database_url.get_secret_value(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()
elif context.config.attributes.get("connection") is not None:
    configure(context.config.attributes["connection"])
else:
    engine = create_engine(Settings().database_url.get_secret_value(), poolclass=pool.NullPool)
    try:
        with engine.connect() as connection:
            configure(connection)
    finally:
        engine.dispose()
