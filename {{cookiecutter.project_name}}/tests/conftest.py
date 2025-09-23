import logging
from pathlib import Path

import dotenv
import pytest
from beartype.claw import beartype_package

logger = logging.getLogger(__name__)

# RUNTIME TYPE CHECKING - only enable during testing
beartype_package("{{cookiecutter.pkg_clean_name}}")


PROJ_ROOT = Path(__file__).parent.parent


@pytest.fixture(scope="session")
def env_values():
    p = PROJ_ROOT / "_local" / ".env"
    if not p.exists():
        raise FileNotFoundError(p)
    return dotenv.dotenv_values(p)
