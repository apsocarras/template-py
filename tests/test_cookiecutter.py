from __future__ import annotations

import shlex
import subprocess

from tests.utils import run_within_dir


def test_bake_project(cookies):
    result = cookies.bake(extra_context={"project_name": "foo-bar"})

    assert result.exit_code == 0
    assert result.exception is None
    assert result.project_path.name == "foo-bar"
    assert result.project_path.is_dir()


def test_using_pytest(cookies, tmp_path):
    with run_within_dir(tmp_path):
        result = cookies.bake()

        # Assert that project was created.
        assert result.exit_code == 0
        assert result.exception is None
        assert result.project_path.name == "my_project"
        assert result.project_path.is_dir()

        # Install the uv environment and run the tests.
        with run_within_dir(str(result.project_path)):
            assert subprocess.check_call(shlex.split("uv sync --group test")) == 0
            assert subprocess.check_call(shlex.split("uv run just test")) == 0
