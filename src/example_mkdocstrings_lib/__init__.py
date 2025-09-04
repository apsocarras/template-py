"""

Welcome to WCK's future python documentation.

Live edits in your python project show up in your web-based docs.

The code for the proxy has to be shared across multiple functions, and
includes other reusable utiltiies for future cloud functions.

Without section-index plugin, init is a separate entry in the nav bar.

With the plugin it just becomes the index/landing page for the library.

TEST! I'M DIFFERENT. I'm different again. Use mkdocs serve --watch src/ for live changes.
Test!

After adding a new file/directory (e.g. projects, projects/__init__.py, projects/foo.py),

* mkdocs build
* mkdocs serve

# Testing MkDown
"""


def hello() -> str:
    return "Hello from example-mkdocstrings-lib!"
