from __future__ import annotations
import logging
import os
import sys
import structlog

def setup_logging() -> None:
    """
    Configure structlog to emit readable key=value logs by default.
    Switch to JSON with LOG_FORMAT=json. Control level with LOG_LEVEL.
    """
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    fmt = os.getenv("LOG_FORMAT", "console")  # "console" or "json"

    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(message)s",
        stream=sys.stdout,
    )

    shared_processors = [
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
    ]

    if fmt == "json":
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer()  # pretty key=val

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            *shared_processors,
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, level, logging.INFO)),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
