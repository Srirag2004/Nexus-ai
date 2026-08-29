from contextlib import asynccontextmanager

import structlog
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import NexusError
from app.core.logging import configure_logging, new_request_id
from app.db.base import Base
from app.db.session import engine, get_db

configure_logging()
logger = structlog.get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Local development stays zero-config; hosted environments use Alembic before startup.
    if settings.app_env == "development":
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
            # Keep the local SQLite demo database compatible with additive schema changes.
            if connection.dialect.name == "sqlite":
                user_columns = await connection.run_sync(lambda sync_connection: {column["name"] for column in inspect(sync_connection).get_columns("users")})
                agent_columns = await connection.run_sync(lambda sync_connection: {column["name"] for column in inspect(sync_connection).get_columns("agent_runs")})
                evaluation_columns = await connection.run_sync(lambda sync_connection: {column["name"] for column in inspect(sync_connection).get_columns("evaluation_runs")})
                if "password_hash" not in user_columns:
                    await connection.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)"))
                if "user_id" not in agent_columns:
                    await connection.execute(text("ALTER TABLE agent_runs ADD COLUMN user_id CHAR(36)"))
                if "user_id" not in evaluation_columns:
                    await connection.execute(text("ALTER TABLE evaluation_runs ADD COLUMN user_id CHAR(36)"))
    logger.info("app_started", env=settings.app_env, provider=settings.ai_provider)
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.include_router(api_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = new_request_id()
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(NexusError)
async def handle_nexus_error(_: Request, exc: NexusError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.get("/")
async def root() -> dict[str, str]:
    return {"name": settings.app_name, "status": "running"}


@app.get("/health")
async def health(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    await db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}
