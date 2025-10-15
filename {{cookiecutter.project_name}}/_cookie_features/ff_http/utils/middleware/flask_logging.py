"""Middleware to log request metadata for flask requests"""

from __future__ import annotations

import contextlib
import logging
import time
import uuid

import flask
from flask import request
from flask.wrappers import Response
from type_cellar import SequenceNotStr as Sequence  # noqa: F401

from ..logging_config import (
    client_ip_var,
    correlation_id_var,
    duration_ms_var,
    http_method_var,
    http_path_var,
    request_id_var,
    status_code_var,
    user_agent_var,
)

logger = logging.getLogger("{{cookiecutter.pkg_clean_name}}_app_json_logger")


def _remote_addr(req: flask.Request) -> str | None:
    """Identify client id (convention: first ip in xff list, if present)"""
    xff = req.access_route
    return xff[0] if xff else req.remote_addr


def install_flask_logging(app: flask.Flask) -> None:
    """Middleware to log request metadata for flask requests

    - Handles setup and tear down (gracefully).
    - Loads session context variables to apply to all logging messages (see RequestContextFilter)
    """

    @app.before_request
    def _before_request() -> None:
        request._start_time = time.perf_counter()  # type: ignore[attr-defined] # pyright: ignore[reportAttributeAccessIssue]

        req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        corr_id = request.headers.get("X-Correlation-ID") or req_id

        _ = request_id_var.set(req_id)
        _ = correlation_id_var.set(corr_id)
        _ = http_method_var.set(request.method)
        _ = http_path_var.set(request.path)
        _ = client_ip_var.set(
            _remote_addr(request)
        )  # note: use ProxyFix when creating app
        _ = user_agent_var.set(request.headers.get("User-Agent"))

        logger.info(
            "HTTP request started",
            extra={
                "event": "http.request.start",
                "content_length": request.content_length,
            },
        )

    @app.after_request
    def _after_request(response: flask.Response) -> Response:
        start = getattr(request, "_start_time", None)
        if start is not None:
            duration_ms_var.set(round((time.perf_counter() - start) * 1000, 3))

        _ = status_code_var.set(response.status_code)

        logger.info(
            "HTTP request completed",
            extra={
                "event": "http.request.end",
                "response_length": response.calculate_content_length(),
            },
        )
        return response

    @app.teardown_request
    def _teardown_request(_exc: BaseException | None) -> None:
        for var in (
            request_id_var,
            correlation_id_var,
            http_method_var,
            http_path_var,
            status_code_var,
            duration_ms_var,
            client_ip_var,
            user_agent_var,
        ):
            with contextlib.suppress(Exception):
                _ = var.set(None)
