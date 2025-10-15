"""Initialize Flask App with middleware and default views"""

from __future__ import annotations

import logging
from collections.abc import Collection
from pathlib import Path

import flask
from type_cellar import SequenceNotStr as Sequence  # noqa: F401
from werkzeug.middleware.proxy_fix import ProxyFix

from .logging_config import load_logging_config
from .middleware.flask_logging import install_flask_logging

_FILE = Path(__file__)
_LOG_CONFIG = _FILE.parent.parent / "logging_config.json"


def create_app(required_secrets: Collection[str]) -> None:
    """FIXME: unfinished app creation helper"""

    load_logging_config(_LOG_CONFIG)
    app = flask.Flask(__name__)

    # Trust the first proxy IP
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)  # type: ignore[method-assign]

    install_flask_logging(app)

    _logger = logging.getLogger("{{cookiecutter.pkg_clean_name}}_app_json_logger")
