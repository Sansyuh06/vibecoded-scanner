import logging
import os
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool, QueuePool

from ..config import settings

logger = logging.getLogger(__name__)

# Database engine configuration
# - For SQLite: use NullPool to avoid threading issues
# - For PostgreSQL: use QueuePool for connection pooling
is_sqlite = "sqlite" in str(settings.DATABASE_URL)
pool_class = NullPool if is_sqlite else QueuePool

engine_kwargs = {
    "echo": settings.DEBUG,
    "future": True,
    "poolclass": pool_class,
    "pool_pre_ping": True,
}

if is_sqlite:
    engine_kwargs["connect_args"] = {"timeout": 10}
else:
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

engine = create_async_engine(
    str(settings.DATABASE_URL),
    **engine_kwargs
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    future=True,
)

Base = declarative_base()


def _sqlite_schema_needs_refresh(connection) -> bool:
    """Detect schema mismatches for SQLite by comparing metadata with existing columns."""
    inspector = inspect(connection)
    existing_tables = inspector.get_table_names()
    if not existing_tables:
        return False

    for table_name, table in Base.metadata.tables.items():
        if table_name not in existing_tables:
            logger.warning("Missing expected table '%s' in SQLite database.", table_name)
            return True

        existing_columns = {col_info['name'] for col_info in inspector.get_columns(table_name)}
        expected_columns = {column.name for column in table.columns}
        missing_columns = expected_columns - existing_columns

        if missing_columns:
            logger.warning(
                "SQLite table '%s' is missing columns: %s",
                table_name,
                ', '.join(sorted(missing_columns))
            )
            return True

    return False


async def get_db():
    """
    Dependency for FastAPI to provide database sessions.
    Ensures proper cleanup on errors.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize or refresh database tables."""
    try:
        async with engine.begin() as conn:
            if is_sqlite and await conn.run_sync(_sqlite_schema_needs_refresh):
                if settings.ENVIRONMENT == "production":
                    raise RuntimeError(
                        "Database schema mismatch detected in production. Please run migrations."
                    )

                logger.warning(
                    "SQLite schema mismatch detected; dropping and recreating all tables."
                )
                await conn.run_sync(Base.metadata.drop_all)

            await conn.run_sync(Base.metadata.create_all)

        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def close_db():
    """Close database connections."""
    try:
        await engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")
