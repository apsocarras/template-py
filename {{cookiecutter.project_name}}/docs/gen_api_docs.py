"""Generate the code reference pages and navigation.

See: https://lukasatkinson.de/dump/2023-08-25-python-docstrings-sphinx/
The author suggests using Jinja templates
    (For example -- the index pages are right now all empty.
    It would be much better if they contained links to submodules.
    Consider the griffoner package for creating templates.)
"""

# ruff: noqa: F401
from __future__ import annotations

from pathlib import Path

import mkdocs_gen_files
from type_cellar import (
    SequenceNotStr as Sequence,  # pyright: ignore[reportUnusedImport]
)

nav = mkdocs_gen_files.Nav()
for path in sorted(Path("src").rglob("*.py")):
    module_path = path.relative_to("src").with_suffix("")
    doc_path = path.relative_to("src").with_suffix(".md")
    full_doc_path = Path("reference", doc_path)

    parts = tuple(module_path.parts)

    if parts[-1] == "__init__":
        parts = parts[:-1]
        doc_path = doc_path.with_name("index.md")
        full_doc_path = full_doc_path.with_name("index.md")

    nav[parts] = doc_path.as_posix()

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        ident = ".".join(parts)
        fd.write(f"::: {ident}")

    mkdocs_gen_files.set_edit_path(full_doc_path, path)

with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
