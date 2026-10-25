"""gng new: create a small Python command-line project, ready to install."""

import keyword
import re
import shlex
import shutil
import sys
from pathlib import Path
from string import Template

from gng import ui

NAME_OK = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")

PYPROJECT = Template('''[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "$name"
version = "0.1.0"
description = "$name: a Python command-line tool"
readme = "README.md"
requires-python = ">=3.9"
dependencies = ["typer"]

[project.optional-dependencies]
dev = ["pytest"]

[project.scripts]
$name = "$package.cli:app"
''')

README = Template('''# $name

A Python command-line tool.

## Install (development)

```
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Use

```
$name
$name hello YOUR_NAME
```

## Test

```
pytest
```
''')

GITIGNORE = '''.venv/
__pycache__/
.pytest_cache/
*.egg-info/
dist/
build/
'''

MAIN = Template('''from $package.cli import app

app()
''')

CLI = Template('''import typer

app = typer.Typer(add_completion=False, help="$name")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        typer.echo("$name is ready. Try: $name hello YOUR_NAME")


@app.command()
def hello(who: str):
    """Say hello."""
    typer.echo(f"Hello, {who}!")
''')

TEST = Template('''from typer.testing import CliRunner

from $package.cli import app

runner = CliRunner()


def test_hello():
    result = runner.invoke(app, ["hello", "Kush"])
    assert result.exit_code == 0
    assert "Hello, Kush!" in result.output
''')


def files_for(name, package):
    """Every file of the new project: relative path -> text."""
    values = {"name": name, "package": package}
    return {
        "pyproject.toml": PYPROJECT.substitute(values),
        "README.md": README.substitute(values),
        ".gitignore": GITIGNORE,
        f"src/{package}/__init__.py": "",
        f"src/{package}/__main__.py": MAIN.substitute(values),
        f"src/{package}/cli.py": CLI.substitute(values),
        "tests/test_cli.py": TEST.substitute(values),
    }


def run(name, directory):
    if not NAME_OK.match(name):
        ui.die(f"'{name}' is not a valid project name",
               "use letters, numbers, - or _, starting with a letter. Example: gng new my-tool")

    package = name.lower().replace("-", "_")
    taken = getattr(sys, "stdlib_module_names", ())
    if keyword.iskeyword(package) or package in taken:
        ui.die(f"'{package}' is already a Python name and would cause confusing imports",
               f"pick another name, like {name}-cli")

    target = Path(directory) / name
    if target.exists():
        ui.die(f"{target} already exists",
               "choose a different name, or remove that folder first")

    files = files_for(name, package)
    try:
        for relative, content in files.items():
            path = target / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    except OSError as error:
        shutil.rmtree(target, ignore_errors=True)
        ui.die(f"could not create {target}: {error.strerror or error}",
               "check that the folder exists and that you can write to it")

    print()
    ui.say("ok", f"created {target}/ ({ui.plural(len(files), 'file')})")
    print()
    ui.note("next:")
    ui.note(f"cd {shlex.quote(str(target))}", indent=4)
    ui.note("python3 -m venv .venv && source .venv/bin/activate", indent=4)
    ui.note('pip install -e ".[dev]"', indent=4)
    ui.note(name, indent=4)
