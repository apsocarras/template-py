"""Use request-scoped context variables for applying request metadata to logger messagges"""

from __future__ import annotations

import json
import logging
import logging.config
from contextvars import ContextVar
from pathlib import Path

from type_cellar import SequenceNotStr as Sequence  # noqa: F401
from typing_extensions import override  # noqa: UP035

# Request-scoped context
request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
correlation_id_var: ContextVar[str | None] = ContextVar("correlation_id", default=None)
http_method_var: ContextVar[str | None] = ContextVar("http_method", default=None)
http_path_var: ContextVar[str | None] = ContextVar("http_path", default=None)
status_code_var: ContextVar[int | None] = ContextVar("status_code", default=None)
duration_ms_var: ContextVar[float | None] = ContextVar("duration_ms", default=None)
client_ip_var: ContextVar[str | None] = ContextVar("client_ip", default=None)
user_agent_var: ContextVar[str | None] = ContextVar("user_agent", default=None)


class RequestContextFilter(logging.Filter):
    """Uses filter to ensure that log records have request data applied from local context"""

    @override
    def filter(self, record: logging.LogRecord) -> bool:
        if not getattr(record, "request_id", None):
            record.request_id = request_id_var.get()
        if not getattr(record, "correlation_id", None):
            record.correlation_id = correlation_id_var.get()

        record.http_method = (
            getattr(record, "http_method", None) or http_method_var.get()
        )
        record.http_path = getattr(record, "http_path", None) or http_path_var.get()
        record.status_code = (
            getattr(record, "status_code", None) or status_code_var.get()
        )
        record.duration_ms = (
            getattr(record, "duration_ms", None) or duration_ms_var.get()
        )
        record.client_ip = getattr(record, "client_ip", None) or client_ip_var.get()
        record.user_agent = getattr(record, "user_agent", None) or user_agent_var.get()

        return True


_DEFAULT_LOGGING_CONFIG = Path(__file__).parent.parent / "logging_config.json"


def load_logging_config(config_path: str | Path | None = None) -> None:
    """Loads the JSON config. Use before initializing logger"""
    path = Path(config_path) if config_path else _DEFAULT_LOGGING_CONFIG
    if not path.exists():
        raise FileNotFoundError(str(path.resolve()))
    with path.open("r", encoding="utf-8") as f:
        cfg = json.load(f)
    logging.config.dictConfig(cfg)
