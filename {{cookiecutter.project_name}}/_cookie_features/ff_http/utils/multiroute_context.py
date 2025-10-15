'''
https://medium.com/google-cloud/use-multiple-paths-in-cloud-functions-python-and-flask-fc6780e560d3

^^ Explanation of how python gcp cloud functions are built on flask and how to add custom routing in functions-framework.
Adapted this code to make it more """pythonic"""
'''

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

import flask
from flask.ctx import RequestContext
from type_cellar import SequenceNotStr as Sequence  # noqa: F401


@contextmanager
def internal_context(
    app: flask.Flask, request: flask.Request
) -> Generator[RequestContext, Any, None]:
    """
    Internal context for our Flask app. Sits "inside" GCP's handling of Flask for us on the backend.
    Handles the routing for GCP instead.
    """
    # Inject data and headers from request into our local flask.Flask app
    internal_ctx: RequestContext = app.test_request_context(
        path=request.full_path,
        method=request.method,
        data=request.get_data(),
        # headers=request.headers, # Don't set here, see note
    )
    ## NOTE: For some reason, data must be injected in the test_request_context call,
    ## NOTE: Headers must be set after.
    # internal_ctx.request.data = request.get_data()
    internal_ctx.request.headers = request.headers

    # Activate context & cleanup when done -- .push() is actually handled automatically by RequestContext in a `with` block anyways
    internal_ctx.push()
    try:
        yield internal_ctx
    finally:
        internal_ctx.pop()
