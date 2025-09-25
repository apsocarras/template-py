from __future__ import annotations

import json
import logging
import logging.config
from http import HTTPStatus
from pathlib import Path

import flask
from flask.typing import ResponseReturnValue
from flask.wrappers import Response

from .utils.multiroute_context import internal_context

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

with open(Path("logging_config.json")) as file:
    config = json.load(file)  # pyright: ignore[reportAny]
logging.config.dictConfig(config)  # pyright: ignore[reportAny]

# This app object allows for multiple endpoints in a functions-framework app.
app = flask.Flask("internal")
# See multiroute_context.py for code on handling custom routing.


@app.route("/healthcheck", methods=["GET"])
def health_check() -> ResponseReturnValue:
    return flask.jsonify({"status": "OK"}), HTTPStatus.OK


@app.route("/echo", methods=["POST"])
def echo() -> ResponseReturnValue:
    """Echo HTTP endpoint (JSON) to act as toy example"""
    try:
        request_json = flask.request.get_json()
        request_args = flask.request.args
        return flask.jsonify(
            {"Received": {"args": request_args, "json": request_json}}
        ), HTTPStatus.OK
    except Exception as e:
        return flask.jsonify(
            {"error": f"Internal error: {e!s}"}
        ), HTTPStatus.INTERNAL_SERVER_ERROR


# === MAIN ENTRY POINT ===
def run(request: flask.Request):
    """
    Main entry point for Cloud Functions.
    Routes requests based on path to the handlers registered with the @app.route decorator.

    NOTE: The name of this function needs to match:
        * `--entry-point` flag when using gcloud functions deploy (makefile or CLI)
        * `--target` flag when running locally with `functions-framework` command
    """

    with internal_context(app, request):
        return_value: Response = app.full_dispatch_request()

    return return_value
