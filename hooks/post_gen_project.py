# pyright: reportAny=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportMissingParameterType=false

"""
Adapted: https://github.com/cookiecutter/cookiecutter/issues/723s
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


PROJECT_ROOT = Path.cwd()
FEATURES_DIR = PROJECT_ROOT / "_cookie_features"


def copy_feature(name: str):
    if (feature_dir := (FEATURES_DIR / name)).exists():
        for item in feature_dir.iterdir():
            dst = PROJECT_ROOT / item.name
            _ = (
                shutil.copytree(item, dst, dirs_exist_ok=True)
                if item.is_dir()
                else shutil.copy2(item, dst)
            )


def main():
    ff = "{{ cookiecutter.ff_type }}".lower()
    match ff:
        case "none":
            pass
        case "http":
            copy_feature("ff_http")
        case "pubsub":
            copy_feature("ff_pubsub")
        case _:
            raise ValueError(ff)

    if "{{cookiecutter.keep_features_dir}}".lower() == "false":
        shutil.rmtree(FEATURES_DIR)


if __name__ == "__main__":
    main()
