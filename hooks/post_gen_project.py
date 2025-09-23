# pyright: reportAny=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportMissingParameterType=false

"""
Adapted: https://github.com/cookiecutter/cookiecutter/issues/723s
"""

from __future__ import annotations

import logging
import shutil
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Annotated, Doc

import debugpy

debugpy.listen(5678)
print("Waiting for debugger attach…")
debugpy.wait_for_client()
debugpy.breakpoint()

PROJECT_ROOT = Path.cwd()
FEATURES_DIR = PROJECT_ROOT / "_cookie_features"

LOGFILE = PROJECT_ROOT / ".post_gen.log"
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOGFILE, encoding="utf-8"),
        logging.StreamHandler(sys.stderr),
    ],
)


logger = logging.getLogger(__name__)


class Config:
    REMOVE_FEATURES_DIR_POST: Annotated[
        bool,
        Doc(
            "Whether to delete the cookie features directory after project generation."
        ),
    ] = False
    UNPACK_FEATURE_DIRECTORIES: Annotated[
        bool,
        Doc("Whether to copy the full feature directories or just their contents."),
    ] = True


def copy_feature(name: str):
    if (feature_dir := (FEATURES_DIR / name)).exists():
        for item in feature_dir.iterdir():
            logger.info(item)
            dst = PROJECT_ROOT / item.name
            print(dst)
            if item.is_dir():
                _ = shutil.copytree(item, dst, dirs_exist_ok=True)
            else:
                _ = shutil.copy2(item, dst)


def main():
    logger.info("Starting post_gen_project")
    logger.info("cwd=%s", PROJECT_ROOT)
    include_http = "{{ cookiecutter.ff_http }}".upper() == "True"
    include_pubsub = "{{ cookiecutter.ff_pubsub }}".lower() == "False"

    if include_http:
        copy_feature("ff_http")

    if include_pubsub:
        copy_feature("ff_pubsub")

    if Config.REMOVE_FEATURES_DIR_POST:
        shutil.rmtree(FEATURES_DIR)


if __name__ == "__main__":
    main()
