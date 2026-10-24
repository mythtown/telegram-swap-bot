from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from bot.config import config


class Base(DeclarativeBase):
    pass


engine = create_async_engine(
    config.database_url,
    echo=False,
    future=True,
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Initializes tables in database and automatically applies missing column migrations."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        def _migrate(sync_conn):
            from sqlalchemy import inspect, text
            insp = inspect(sync_conn)
            tables = insp.get_table_names()

            if "users" in tables:
                user_cols = [c["name"] for c in insp.get_columns("users")]
                if "referred_by_id" not in user_cols:
                    sync_conn.execute(text("ALTER TABLE users ADD COLUMN referred_by_id BIGINT"))
                if "referrals_count" not in user_cols:
                    sync_conn.execute(text("ALTER TABLE users ADD COLUMN referrals_count INTEGER DEFAULT 0"))
                if "qualified_referrals_count" not in user_cols:
                    sync_conn.execute(text("ALTER TABLE users ADD COLUMN qualified_referrals_count INTEGER DEFAULT 0"))
                if "has_qualified_referral" not in user_cols:
                    sync_conn.execute(text("ALTER TABLE users ADD COLUMN has_qualified_referral BOOLEAN DEFAULT 0"))

            if "creatives" in tables:
                creative_cols = [c["name"] for c in insp.get_columns("creatives")]
                if "creative_type" not in creative_cols:
                    sync_conn.execute(text("ALTER TABLE creatives ADD COLUMN creative_type VARCHAR(16) DEFAULT 'text'"))

        await conn.run_sync(_migrate)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency helper to yield async database session."""
    async with async_session_factory() as session:
        yield session
