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
gng folder notes       # create a folder in the current location
gng folder assets -d ~/Projects  # choose a parent folder
gng ls [path]          # list entries in a folder, including hidden entries
gng open [path]        # change this terminal's directory (requires zsh setup)
gng cd [path]          # same as gng open
gng touch notes.txt    # create an empty file (or give several paths)
gng rm notes.txt       # delete files; asks for confirmation
gng rmdir old-notes    # delete a folder and its contents; asks for confirmation
gng rename old.txt new.txt  # rename a file in the same folder
gng new my-tool        # start a new Python CLI project
gng doctor             # check your setup (Python, venv, git, terminal)
gng todo [path]        # list TODO / FIXME notes in code
gng clean [path]       # remove cache folders (--dry-run to preview, --yes to skip the question)
gng --help             # list every command
```

Set `NO_COLOR=1` to turn colors off, or `GNG_ASCII=1` to use plain ASCII characters.

## Terminal directory commands (zsh)

A Python command cannot change the working directory of its parent terminal. To use `gng open` or `gng cd` as directory-changing commands, load the zsh integration:

```bash
echo 'source /Users/kushagramishra/Documents/gng-cli/shell/gng.zsh' >> ~/.zshrc
source ~/.zshrc
```

Then use `gng open ~/Projects` or `gng cd ~/Projects`. With no path, either command stays in the current directory. Other GNG commands continue to use the Python CLI.

## Project layout

```
src/gng/
  cli.py        the commands, kept thin
  banner.py     the banner, colors and terminal detection
  ui.py         shared output helpers (markers, errors)
  commands/     one file per command: folder, filesystem, new, doctor, todo, clean
tests/
shell/
  gng.zsh      zsh integration for changing directories
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
