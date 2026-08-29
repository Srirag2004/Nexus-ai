from collections.abc import AsyncGenerator

from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

settings = get_settings()


def _async_database_options() -> tuple[str, dict[str, str]]:
    """Translate Neon/libpq SSL query parameters for asyncpg."""
    database_url = settings.database_url
    connect_args: dict[str, str] = {}
    if database_url.startswith("postgresql+asyncpg://"):
        url = make_url(database_url)
        query = dict(url.query)
        ssl_mode = query.pop("sslmode", None)
        query.pop("channel_binding", None)
        if ssl_mode in {"require", "verify-ca", "verify-full"}:
            connect_args["ssl"] = "require"
        database_url = url.set(query=query).render_as_string(hide_password=False)
    return database_url, connect_args


database_url, connect_args = _async_database_options()
engine = create_async_engine(database_url, connect_args=connect_args, future=True, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
