"""credit to https://github.com/fpgmaas/cookiecutter-uv for inspiration on these tests"""

from __future__ import annotations

import os
import shlex
import subprocess

import pytest

from tests.utils import run_within_dir


def test_bake_project(cookies):
    result = cookies.bake(extra_context={"project_name": "foo-bar"})

    assert result.exit_code == 0
    assert result.exception is None
    assert result.project_path.name == "foo-bar"
    assert result.project_path.is_dir()


@pytest.mark.parametrize("on", ((True, False)))
def test_include_ff_http(cookies, on: bool):
    feature_setting = "http" if on else "none"

    result = cookies.bake(extra_context={"ff_type": feature_setting})
    assert result.exit_code == 0

    assert os.path.isfile(f"{result.project_path}/app.py") == on
    assert os.path.isfile(f"{result.project_path}/utils/multiroute_context.py") == on
    assert os.path.isfile(f"{result.project_path}/utils/__init__.py") == on


@pytest.mark.parametrize("on", ((True, False)))
def test_include_ff_pubsub(cookies, on: bool):
    feature_setting = "pubsub" if on else "none"

    result = cookies.bake(extra_context={"ff_type": feature_setting})
    assert result.exit_code == 0

    assert os.path.isfile(f"{result.project_path}/app.py") == on
    assert os.path.isfile(f"{result.project_path}/utils/deduping.py") == on
    assert os.path.isfile(f"{result.project_path}/utils/__init__.py") == on


@pytest.mark.parametrize("on", ((True, False)))
def test_keep_features_dir(cookies, on: bool):
    result = cookies.bake(extra_context={"keep_features_dir": on})
    assert result.exit_code == 0

    assert os.path.isdir(f"{result.project_path}/_cookie_features") == on


@pytest.mark.parametrize(
    "extra,value",
    (
        (None, None),
        (
            "ff_type",
            "http",
        ),
        (
            "ff_type",
            "pubsub",
        ),
    ),
)
def test_justfile(extra, value, cookies, tmp_path):
    with run_within_dir(tmp_path):
        # result = cookies.bake()
        extra_args = {extra: value} if extra else None
        result = cookies.bake(extra_context=extra_args)

        # Assert that project was created.
        assert result.exit_code == 0
        assert result.exception is None
        assert result.project_path.name == "my_project"
        assert result.project_path.is_dir()

        if extra is not None:
            assert os.path.isfile(f"{result.project_path}/app.py")
            assert os.path.isdir(f"{result.project_path}/utils")

            # Install the uv environment and run the tests.
            with run_within_dir(str(result.project_path)):
                assert (
                    subprocess.check_call(
                        shlex.split("uv sync --group test --group dev")
                    )
                    == 0
                )
                assert subprocess.check_call(shlex.split("uv run just test")) == 0
                assert subprocess.check_call(shlex.split("uv run just cov")) == 0
                assert subprocess.check_call(shlex.split("just test")) == 0
                assert subprocess.check_call(shlex.split("just cov")) == 0

                # assert subprocess.check_call(shlex.split("just deps")) == 0
                assert subprocess.check_call(shlex.split("just lint")) == 0
                assert subprocess.check_call(shlex.split("just fix")) == 0
                assert subprocess.check_call(shlex.split("just type_src")) == 0
                assert subprocess.check_call(shlex.split("just type_utils")) == 0
                assert subprocess.check_call(shlex.split("just type_app")) == 0
                assert subprocess.check_call(shlex.split("just types")) == 0
                assert subprocess.check_call(shlex.split("just dist")) == 0
                assert subprocess.check_call(shlex.split("just py311")) == 0
                # assert subprocess.check_call(shlex.split("just py_312")) == 0
