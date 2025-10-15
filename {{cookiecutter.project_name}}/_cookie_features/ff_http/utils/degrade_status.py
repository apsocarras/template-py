"""Contains reusable class-based flask views for reporting the status of the app"""
# ruff: noqa: UP035

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from enum import Enum
from http import HTTPStatus

import flask
from beartype.typing import Any, Callable, Protocol, TypeAlias
from flask.typing import ResponseReturnValue, RouteCallable
from flask.views import View
from nobeartype import NoBearType
from type_cellar import JSONType
from type_cellar import SequenceNotStr as Sequence  # noqa: F401
from typing_extensions import ClassVar, TypeVar, overload, override

nobeartype = NoBearType()

logger = logging.getLogger(__name__)

App: TypeAlias = flask.Flask
Response: TypeAlias = flask.Response


DEGRADE_STATUS_KEY = "X-AppDegradeStatus"


class AppDegradeStatusType(Enum):
    """Codes for degrade statuses applicable to the app"""

    MISSING_SECRETS = "Missing App Secrets"
    PUBLISHER_CLIENT_FAIL = "Failed to connect Pub/Sub"
    MISSING_TOPIC = "Missing Pub/Sub Topic"
    PUBLISH_FAILED = "Failed to publish pub/sub"

    @override
    def __str__(self) -> str:
        return self.value


class HasAppDegradeStatus(Protocol):
    """Simplified proto for flask.Flask"""

    config: flask.Config


def get_degrade_statuses(
    app: HasAppDegradeStatus,
) -> set[AppDegradeStatusType]:
    """Read the degrade statuses attach to a flask app"""
    if not app.config.get(DEGRADE_STATUS_KEY, set()):
        app.config[DEGRADE_STATUS_KEY] = set()
    return app.config[DEGRADE_STATUS_KEY]  # type: ignore[no-any-return] # pyright: ignore[reportUnknownVariableType]


def add_degrade_status(app: HasAppDegradeStatus, status: AppDegradeStatusType) -> None:
    """Attach a degrade status to a flask app"""
    get_degrade_statuses(app).add(status)


def remove_degrade_status(
    app: HasAppDegradeStatus, status: AppDegradeStatusType
) -> None:
    """Remove a degrade status from a flask app"""
    get_degrade_statuses(app).remove(status)


def app_is_degraded(app: HasAppDegradeStatus) -> set[AppDegradeStatusType]:
    """Alias for get_degrade_statuses"""
    return get_degrade_statuses(app)


def app_has_status(app: HasAppDegradeStatus, status: AppDegradeStatusType) -> bool:
    """Check if the app has a given degrade status"""
    return status in get_degrade_statuses(app)


T = TypeVar("T", bound=Any)
R = TypeVar("R", bound=Any)


@overload
def degrade_app_if_fail(
    app: HasAppDegradeStatus,
    callable_: Callable[..., T],
    status_if_fail: AppDegradeStatusType,
    return_if_error: None,
    fail_condition: Callable[[T], bool] | None = None,
    logger_callback: Callable[..., Any] | None = None,
) -> T | None: ...


@overload
def degrade_app_if_fail(
    app: HasAppDegradeStatus,
    callable_: Callable[..., T],
    status_if_fail: AppDegradeStatusType,
    return_if_error: R,
    fail_condition: Callable[[T], bool] | None = None,
    logger_callback: Callable[..., Any] | None = None,
) -> T | R: ...


def degrade_app_if_fail(
    app: HasAppDegradeStatus,
    callable_: Callable[..., T],
    status_if_fail: AppDegradeStatusType,
    return_if_error: R | None = None,
    fail_condition: Callable[[T], bool] | None = None,
    logger_callback: Callable[..., Any] | None = None,
) -> T | R | None:
    """Wrap any function call with a success/fail check. When failed, applies a chosen fail status on your app.

    Captures/logs exceptions. Intended to work with a healthcheck/ endpoint used to monitor the degrade status of the app.

    Args:
        app (App): Flask app.
        callable_ (Callable[..., T]): Arbitrary callable to execute.
        status_if_fail (AppDegradeStatusType): The fail status to apply.
        return_if_error (R | None, optional): What to return if an error was thrown during your callable or fail condition. Defaults to None.
        fail_condition (Callable[[T], bool] | None, optional): A check to pass on your callable which defines its failture condition. Defaults to None.
        logger_callback (Callable[..., Any] | None, optional): Logger function. Defaults to logger.exception

    Returns:
        T | R | None: Either the expected return of the callable or the return type in case of error.


    ```pycon
    >>> from wck_python_utils.types.enums import AppDegradeStatusType
    >>> from wck_python_utils.cloud_functions.app_status import get_degrade_statuses, add_degrade_status, remove_degrade_status

    >>> class MockFlask:
    ...     def __init__(self):
    ...         self.config = {}

    >>> mock_app = MockFlask()
    >>> add_degrade_status(mock_app, AppDegradeStatusType.MISSING_TOPIC)
    >>> get_degrade_statuses(mock_app)
    {<AppDegradeStatusType.MISSING_TOPIC: 'Missing Pub/Sub Topic'>}

    >>> impossible_division: float | str = degrade_app_if_fail(
    ...     app=mock_app,
    ...     callable=lambda: -1 / 0,
    ...     status_if_fail=AppDegradeStatusType.PUBLISHER_CLIENT_FAIL,
    ...     return_if_error="Whoops!",
    ...     fail_condition=None,
    ... )

    >>> assert impossible_division == "Whoops!"
    >>> assert app_has_status(mock_app, AppDegradeStatusType.PUBLISHER_CLIENT_FAIL)

    >>> failed_modulo: int | str = degrade_app_if_fail(
    ...    app=mock_app,
    ...    callable=lambda: 13 % 4,
    ...    status_if_fail=AppDegradeStatusType.MISSING_TOPIC,
    ...    return_if_error="Whoops!",
    ...    fail_condition=lambda x: x > 4,
    ... )

    >>> assert failed_modulo == (13 % 4)
    >>> assert app_has_status(mock_app, AppDegradeStatusType.MISSING_TOPIC)

    ```
    """

    res_logger = lambda: logger.exception(  # noqa: E731
        {
            "event": "degrade_app_check",
            "status": "error",
            "details": {"degrade_status": str(status_if_fail)},
        }
    )

    try:
        result = callable_()
        if fail_condition and fail_condition(result):
            add_degrade_status(app, status_if_fail)
    except Exception:
        add_degrade_status(app, status_if_fail)
        res_logger()
        return return_if_error
    else:
        res_logger()
        return result


class FrozenInstantiableAppView(View, ABC):
    """
    Instance-level API for `flask.views.View`. Shorter to register views vs the default class-level API

    WARNING: The view will not update if you change any value from what it was at initialization.
    WARNING: Different views cannot be added via `add_url_rule` to the same app object at the same endpoint.

    See :doc:`views` for a detailed guide (TL;DR class-based API for isolated, testable, reuseable endpoint logic in apps).
    Set cls :attr:`init_every_request` to ``False`` for efficiency, unless you need to store request-global data on ``self``.


    ```pycon
    >>> from flask import Flask
    >>> from typing_extensions import override

    >>> class HelloView(FrozenInstantiableAppView):
    ...     def __init__(self, greeting: str = "Hello", name: str = "World"):
    ...         super().__init__(greeting=greeting, name=name)
    ...         self.greeting: str = greeting
    ...         self.name: str = name
    ...
    ...     @override
    ...     def dispatch_request(self):
    ...         return f"{self.greeting}, {self.name}!"

    >>> app = Flask(__name__)
    >>> view = HelloView(greeting="Hi", name="Alex")
    >>> app.add_url_rule("/hello", view_func=view.view("/hello"))
    >>> with app.test_client() as client:
    ...     rv = client.get("/hello")
    ...     rv.status_code
    200

    >>> rv.text
    'Hi, Alex!'

    ```
    """

    init_every_request: ClassVar[bool] = False

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize FrozenInstantiableAppView"""
        super().__init__()

        ## This is more flexible and safer than using inspect.signature()
        ## We capture every user provided value in __init__ this way regardless of its name
        ##   (*args and **kwargs placeholders obscure real values)

        self._args: tuple[Any, ...] = tuple(arg for arg in args)
        self._kwarg_vals: tuple[Any, ...] = tuple(v for v in kwargs.values())

    @abstractmethod
    @override
    @nobeartype
    def dispatch_request(self) -> ResponseReturnValue: ...

    @nobeartype
    def view(self, route: str) -> RouteCallable:
        """
        This method goes through the saved values from `__init__`.
        It then calls the class method and passes in these values to get a `RouteCallable`.

        (No way am I going to make a new class with new class attributes and copy-paste the required arguments to `__init__`
        into `.as_view()` again and again every time I want to add a view. Garbage!)
        """
        return self.__class__.as_view(route, *self._args, *self._kwarg_vals)


class HealthCheckView(FrozenInstantiableAppView):
    """
    Factory for making a view on a App app for a healthcheck

    ```pycon
    >>> from flask import Flask

    >>> app = Flask(__name__)
    >>> always_healthy = HealthCheckView(fail_condition=lambda: False, foo="bar")
    >>> always_sick = HealthCheckView(
    ...     fail_condition=lambda: True,
    ...     fail_response_data=lambda: "I don't feel so good."
    ... )
    >>> app.add_url_rule("/healthcheck", view_func=always_healthy.view('/healthcheck'))
    >>> app.add_url_rule("/boo-boo", view_func=always_sick.view('/boo-boo'))

    >>> with app.test_client() as client:
    ...    rv = client.get("/healthcheck")
    ...    rv.status_code
    200

    ...    rv.get_json()
    {'status': 'healthy', 'details': {'foo': 'bar'}}

    ...    rv2 = client.get('/boo-boo')
    ...    rv2.status_code
    500
    ...    rv2.get_json()
    {'status': 'degraded', 'details': {'failure': "I don't feel so good."}}

    ```

    """

    methods = ["GET"]  # noqa: RUF012

    def __init__(
        self,
        fail_condition: Callable[..., bool],
        fail_response_data: Callable[..., JSONType] = lambda: {},
        **other_response_data: JSONType,
    ) -> None:
        self.fail_condition: Callable[..., bool] = fail_condition
        self.fail_response_data: Callable[..., JSONType] = fail_response_data
        self.other_response_data: dict[str, JSONType] = other_response_data
        super().__init__(
            fail_condition=fail_condition, fail_response_data=fail_response_data
        )

    @override
    @nobeartype
    def dispatch_request(self) -> ResponseReturnValue:
        failed = self.fail_condition()
        status, code = (
            ("healthy", HTTPStatus.OK)
            if (not failed)
            else ("degraded", HTTPStatus.INTERNAL_SERVER_ERROR)
        )
        resp_data: dict[str, JSONType] = {"status": status}
        resp_data["details"] = self.other_response_data
        if failed:
            resp_data["details"] = {"failure": self.fail_response_data()}

        return flask.jsonify(resp_data), code


class AppDegradeView(HealthCheckView):
    """

    ```pycon
    >>> from flask import Flask
    >>> from wck_python_utils.types.enums import AppDegradeStatusType
    >>> from wck_python_utils.cloud_functions.app_status import (
    ...        add_degrade_status, remove_degrade_status, get_degrade_statuses
    ...    )

    >>> app = Flask(__name__)
    >>> degrade_view = AppDegradeView(app)
    >>> add_degrade_status(app, status=AppDegradeStatusType.MISSING_TOPIC)
    >>> app.add_url_rule("/healthcheck", view_func=degrade_view.view('/healthcheck'))
    >>> with app.test_client() as client:
    ...    rv = client.get("/healthcheck")
    ...    rv.status_code
    500

    ...    rv.get_json()
    {'details': {'failure': ['Missing Pub/Sub Topic']}, 'status': 'degraded'}

    >>> remove_degrade_status(app, AppDegradeStatusType.MISSING_TOPIC)
    >>> with app.test_client() as client:
    ...    rv = client.get("/healthcheck")
    ...    rv.get_json()
    {'details': {}, 'status': 'healthy'}


    ```

    """

    init_every_request = False

    def __init__(self, app: App, **other_response_data: JSONType) -> None:
        self.app: App = app
        super().__init__(
            fail_condition=lambda: bool(app_is_degraded(self.app)),
            fail_response_data=lambda: [str(s) for s in get_degrade_statuses(self.app)],
            **other_response_data,
        )

    @override
    @nobeartype
    def view(self, route: str) -> RouteCallable:
        return self.__class__.as_view(route, self.app)


def attach_degrade_status_header(app: App) -> App:
    """
    Enable a Flask app to attach AppDegradeStatus messages to its response headers.

    ```pycon
    >>> from flask import Flask
    >>> from typing_extensions import override
    >>> from wck_python_utils.types.enums import AppDegradeStatusType
    >>> from wck_python_utils.cloud_functions.app_status import FrozenInstantiableAppView, add_degrade_status

    >>> class HelloView(FrozenInstantiableAppView):
    ...     def __init__(self, greeting: str = "Hello", name: str = "World"):
    ...         super().__init__(greeting=greeting, name=name)
    ...         self.greeting: str = greeting
    ...         self.name: str = name
    ...
    ...     @override
    ...     def dispatch_request(self):
    ...         return f"{self.greeting}, {self.name}!"

    >>> app = Flask(__name__)
    >>> view = HelloView(greeting="Hi", name="Alex")
    >>> app.add_url_rule("/hello", view_func=view.view("/hello"))
    >>> add_degrade_status(app, AppDegradeStatusType.MISSING_TOPIC)
    >>> app = attach_degrade_status_header(app)

    >>> app = attach_degrade_status_header(app)
    >>> with app.test_client() as client:
    ...    rv = client.get("/hello")
    ...    rv.text
    'Hi, Alex!'

    ...    assert rv.headers.get('X-AppDegradeStatus') == '["Missing Pub/Sub Topic"]'

    ```
    """

    @app.after_request
    def _attach_status(response: Response) -> Response:
        status_info: set[AppDegradeStatusType] = get_degrade_statuses(app)
        if status_info:
            response.headers[DEGRADE_STATUS_KEY] = json.dumps(
                [str(s) for s in status_info]
            )
        return response

    return app


if __name__ == "__main__":
    import doctest

    _ = doctest.testmod()
