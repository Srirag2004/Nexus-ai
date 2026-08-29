import logging
import sys
from contextvars import ContextVar
from uuid import uuid4

import structlog

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")


def configure_logging() -> None:
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=logging.INFO)
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    )


def new_request_id() -> str:
    request_id = str(uuid4())
    request_id_ctx.set(request_id)
    structlog.contextvars.bind_contextvars(request_id=request_id)
    return request_id

