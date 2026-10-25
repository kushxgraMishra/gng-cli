# GNG

A playful, cyberpunk-flavored developer toolkit for Python. Say it like the letters: **G-N-G**.

Run `gng` to get a terminal-sized wordmark and a growing set of small tools for everyday project work.

## Commands

| Command | What it does |
|---|---|
| `gng` | Show the banner and welcome screen |
| `gng new NAME [--dir PATH]` | Create a ready-to-install Python CLI project |
| `gng doctor` | Check Python, virtual environment, pip, Git, and terminal support |
| `gng todo [PATH]` | Find TODO, FIXME, HACK, and XXX notes in code comments |
| `gng clean [PATH]` | Preview or remove Python cache folders |
| `gng folder NAME [--dir PATH]` | Create a folder without overwriting an existing one |
| `gng ls [PATH]` | List the direct contents of a folder, including hidden entries |
| `gng touch FILE...` | Create one or more empty files without overwriting existing entries |
| `gng rm FILE... [--yes]` | Delete one or more files after confirmation |
| `gng rmdir FOLDER [--yes]` | Delete a folder and its contents after confirmation |
| `gng rename FILE NEW_NAME` | Rename a file in the same folder |
| `gng open [PATH]` / `gng cd [PATH]` | Change the current terminal directory (zsh integration required) |
| `gng --help` | Show command help |

Run `gng COMMAND --help` for options and usage details.

## Requirements

- Python 3.9 or newer
- macOS, Linux, or Windows for the Python commands
- zsh for the `gng open` and `gng cd` shell integration

## Install for development

From the project folder, create and activate a virtual environment, then install GNG in editable mode:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
gng
```

Editable mode makes changes to the project code available without reinstalling. Activate `.venv` again in each new terminal before using this development install.

## Install for use from any folder

[pipx](https://pipx.pypa.io/latest/how-to/install-pipx/) installs command-line tools in isolated environments. Once pipx is installed, run this from the GNG project folder:

```bash
pipx install --editable .
```

The editable install uses this local checkout, so code changes take effect the next time you run `gng`. If you change dependencies or install metadata in `pyproject.toml`, reinstall with:

```bash
pipx install --editable . --force
```

To remove this install, run `pipx uninstall gng`.

## File and folder commands

### Create and list

```bash
gng folder notes
gng folder assets --dir ~/Projects
gng ls
gng ls ~/Projects
```

`gng ls` lists the entries immediately inside the selected folder. Hidden entries are included; directories are shown with a trailing slash. `gng folder` creates one folder inside the current directory or the parent selected with `--dir`.

### Create, delete, and rename files

```bash
gng touch notes.txt draft.md
gng rm notes.txt draft.md
gng rm notes.txt --yes
gng rename draft.md final.md
```

`touch` creates empty files and refuses to replace existing files. `rm` only deletes files (not directories) and asks before deleting. Use `--yes` or `-y` to confirm without a prompt. `rename` changes a file’s name in its current folder and refuses to overwrite an existing entry.

### Delete a folder

```bash
gng rmdir old-notes
gng rmdir old-notes --yes
```

`rmdir` removes the selected folder and everything inside it after confirmation. It refuses to remove your home folder, the filesystem root, your current directory, or a parent of your current directory. It refuses a symbolic link as the target and does not follow links found inside the folder.

## Change directory in the current terminal

A Python process cannot change the working directory of its parent shell. GNG provides a small zsh function so `gng open` and `gng cd` behave like `cd`:

```bash
source /path/to/gng-cli/shell/gng.zsh
gng open ~/Projects
```

To enable it in every zsh terminal, add the `source` line to `~/.zshrc`, using the actual path to your GNG checkout, then reload the file:

```bash
source ~/.zshrc
```

With no path, `gng open` and `gng cd` stay in the current directory. The shell function forwards all other commands to the Python CLI.

## `gng new`

```bash
gng new my-tool
gng new my-tool --dir ~/Projects
```

Creates a starter Python CLI project:

```text
my-tool/
├── pyproject.toml
├── README.md
├── .gitignore
├── src/my_tool/
│   ├── __init__.py
│   ├── __main__.py
│   └── cli.py
└── tests/test_cli.py
```

Project names must start with a letter and contain only letters, numbers, hyphens, or underscores. GNG refuses Python keywords, standard-library module names, and existing destination folders.

## `gng doctor`

```bash
gng doctor
```

Checks the Python interpreter running GNG, whether a virtual environment is active, pip and Git availability, terminal width, and color/character support. Missing or old Python causes a non-zero exit; setup warnings include a suggested next step.

## `gng todo`

```bash
gng todo
gng todo src
gng todo app.py
```

Finds `TODO`, `FIXME`, `HACK`, and `XXX` tags after common comment markers such as `#`, `//`, `/*`, and `<!--`. It scans supported source files and skips `.git`, virtual environments, `node_modules`, caches, `dist`, and `build` folders.

## `gng clean`

```bash
gng clean --dry-run
gng clean
gng clean ~/Projects/my-tool --yes
```

Only removes regenerable Python tool caches: `__pycache__`, `.pytest_cache`, `.mypy_cache`, and `.ruff_cache`. It skips `.git`, virtual environments, and `node_modules`, and does not follow symlinks. Without a terminal, deletion requires `--yes`.

## Terminal appearance

The banner chooses the largest layout that fits, leaving room around the edges:

| Terminal width | Banner |
|---|---|
| 57 columns or more | Double outer frame around the framed wordmark |
| 41–56 columns | Framed wordmark |
| 23–40 columns | Compact wordmark in a small frame |
| Under 23 columns | Plain `[ GNG ]` text |

When output is piped, GNG prints a plain status line instead of the decorative banner.

| Variable | Effect |
|---|---|
| `NO_COLOR` | Any non-empty value disables color |
| `GNG_ASCII` | Any non-empty value uses ASCII-compatible characters |
| `COLUMNS` | Overrides the terminal width GNG detects |
| `COLORTERM`, `TERM` | Select the color palette; `TERM=dumb` disables color |

## Troubleshooting

**`gng: command not found`** — Activate the development environment, or install GNG with pipx and ensure pipx’s app directory is on your `PATH`. See the [pipx installation guide](https://pipx.pypa.io/latest/how-to/install-pipx/).

**`gng open` does not change directory** — Confirm the zsh integration is sourced in `~/.zshrc`, then run `source ~/.zshrc` in the current terminal.

**The banner is too small** — Run `gng doctor` and check the reported terminal width. If `COLUMNS` is stale, run `unset COLUMNS` or set it to the correct width for that command.

**Box or block characters look wrong** — Run `GNG_ASCII=1 gng`.

**No colors appear** — Check that `NO_COLOR` is unset and that output is going to a real terminal rather than a pipe.

## Project layout

```text
src/gng/
├── cli.py                 Typer commands and entry point
├── banner.py              Wordmark, color palette, and terminal rendering
├── ui.py                  Shared status messages and errors
└── commands/
    ├── clean.py           Cache cleanup
    ├── doctor.py          Environment checks
    ├── filesystem.py      Listing and file operations
    ├── folder.py          Folder creation
    ├── new.py             Python CLI project scaffolding
    └── todo.py            TODO/FIXME scanning
shell/
└── gng.zsh                zsh integration for directory changes
tests/
├── test_banner.py
└── test_commands.py
```

## Development checks

Install the development dependencies with `python -m pip install -e ".[dev]"`, then run:

```bash
pytest
```
