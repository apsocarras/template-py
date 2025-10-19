# template-py

CLI template for generating a new python project. Contains GCP-focused add-ons.

## Setup/Usage

Requires:

* [`uv`](https://docs.astral.sh/uv/) - The gold standard for Python package management

* [`just`](https://github.com/casey/just) - `Make`-like command runner

```bash
# Activate venv and install cookiecutter 
uv venv 
source .venv/bin/activate
uv pip install cookiecutter 

# Open interactive prompt: name your project and choose from the options
cookiecutter https://github.com/apsocarras/template-py.git 
 
```

## Features

### General

* Python 3.11 - Python3.12 (the versions I use at work)
* `src/` layout, with `docs`, `dev`, and `test` dependency groups

* Optional `GCP` python cloud function add-ons:
  * [`ff_http/`]({{cookiecutter.project_name}}/_cookie_features/ff_http): A `functions-framework` flask app with a custom [shim]({{cookiecutter.project_name}}/_cookie_features/ff_http/utils/multiroute_context.py) for multi-route request dispatch. Includes useful flask utilities for logging, status checks, etc.
  * [`ff_pubsub/`]({{cookiecutter.project_name}}/_cookie_features/ff_pubsub):  Alternatively, an example app for a pub-sub driven function.
  * GCP deployment commands (see [`justfile`](/{{cookiecutter.project_name}}/justfile))

* [`attrs`](https://www.attrs.org/en/stable/) supremacy (🚫🫸🏻 [pydantic hegemony](https://threeofwands.com/why-i-use-attrs-instead-of-pydantic/))

### Tools

#### Code formatting and Linting: [`ruff`](https://astral.sh/ruff)

#### Documentation: [`mkdocs`](https://mkdocstrings.github.io/)

#### Type Checking

* [`mypy`](https://mypy.readthedocs.io/en/stable/) - Static type checking (CLI & CI/CD)
* [`pyright`](https://docs.basedpyright.com/) - Static type checking (IDE/LSP)
* [`beartype`](https://beartype.readthedocs.io/en/latest/) - Runtime type checking (test suite)

#### Depdendencies

* [`deptry`](https://deptry.com/rules-violations/) - Guards against dependency vulnerabilities

#### Testing

[`tests/`]({{cookiecutter.project_name}}/tests/smoke_test.py):

* [`pytest`](https://docs.pytest.org/en/stable/) (obviously) with [`coverage`](https://coverage.readthedocs.io/en/7.11.0/)
  * Also runs any [`doctests`](https://docs.python.org/3/library/doctest.html) in `src/`
* [`testmon`](https://testmon.org) - Run only affected tests (used pre-push)
* [`hypothesis`](https://hypothesis.readthedocs.io/en/latest/) and [`mimesis`](https://mimesis.name/master/) for mock data generation

  <!-- * TODO: At some point I will add some-commonly used data-generation helpers which use these packages. -->

#### CI/CD

* [`pre-commit`]({{cookiecutter.project_name}}/.pre-commit-config.yaml)  
  * [`testmon`](https://testmon.org)
  * [`gitleaks`](https://gitleaks.io/) - Scans for secrets  
  * Lock `requirements.txt` to `pyproject.toml`
* [`.github/`]({{cookiecutter.project_name}}/.github) actions
  * [CI]({{cookiecutter.project_name}}/.github/workflows/ci.yaml) - run test and code quality suite with `just`
  * [CD]({{cookiecutter.project_name}}/.github/workflows/release.yaml) - publish to pypi

#### Editor

* [`.vscode/`](.vscode)
  * `launch.json` with python debugger presets
  * `settings.json` with format on save
    * Requires the `ruff` VS code extension
  * No `devcontainer.json` (might add later)

## How it works

[`cookiecutter`](https://www.cookiecutter.io/) is a python package for quickly spinning-up projects from a template.

Here's how to make your own project templates with it:

1. Create the project file system layout
2. Define user input options in a `cookiecutter.json` file.
3. Insert placeholders (`{{ cookiecutter.XXX }}`) throughout your template which match these user inputs.
4. When executed, `cookiecutter` will:
    * Open a cli interface based on the json manifest
    * Collect user input
    * Use [jinja](https://jinja.palletsprojects.com/en/stable/) to replace these placeholders with input
    * Run any post-generation hooks you define yourself

Note that `{{` and `}}` will make `jinja` attempt to replace anything enclosed within. Block that behavior with `{%raw%}`/`{%endraw%}` escape block.
