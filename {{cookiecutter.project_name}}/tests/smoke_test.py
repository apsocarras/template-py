"""
"Smoke tests" are tests that only check basic aspects of the package.
They point to something more fundamentally wrong in your setup.
"""

from __future__ import annotations

import importlib
import pkgutil
from collections.abc import Iterator


def iter_modules(package) -> Iterator[pkgutil.ModuleInfo]:
    pkg = importlib.import_module("{{cookiecutter.pkg_clean_name}}")
    return pkgutil.walk_packages(pkg.__path__, pkg.__name__ + ".")


def test_all_imports():
    """Test all the modules in the package import successfully"""

    def import_error(name: str) -> Exception | None:
        try:
            importlib.import_module(name)
            return None
        except Exception as e:
            return e

    import_errors = {
        mod.name: mod_error
        for mod in iter_modules("{{cookiecutter.pkg_clean_name}}")
        if (mod_error := import_error(mod.name)) is not None
    }

    assert not import_errors, f"Failed imports: {import_errors}"
