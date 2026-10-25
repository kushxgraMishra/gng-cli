# GNG

A playful, cyberpunk-flavored developer toolkit for Python.

## Install (development)

```
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Use

```
gng                    # banner and welcome screen
gng new my-tool        # start a new Python CLI project
gng doctor             # check your setup (Python, venv, git, terminal)
gng todo [path]        # list TODO / FIXME notes in code
gng clean [path]       # remove cache folders (--dry-run to preview, --yes to skip the question)
gng --help             # list every command
```

Set `NO_COLOR=1` to turn colors off, or `GNG_ASCII=1` to use plain ASCII characters.

## Project layout

```
src/gng/
  cli.py        the commands, kept thin
  banner.py     the banner, colors and terminal detection
  ui.py         shared output helpers (markers, errors)
  commands/     one file per command: new, doctor, todo, clean
tests/
```

## Add a command

1. Create `src/gng/commands/mycommand.py` with a `run(...)` function.
2. In `cli.py`, import it and add a small `@app.command()` function that calls `run`.
3. Add a line to `COMMANDS` in `banner.py` so it shows on the welcome screen.
4. Add a test in `tests/`.

## Test

```
pytest
```
