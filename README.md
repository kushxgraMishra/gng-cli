# GNG

GNG is a small Python developer toolkit CLI. Its terminal landing screen features a custom block-letter **GNG** wordmark, a neon cyan and magenta palette, and a compact layout that adapts to terminal width. The first command, `doctor`, reports which Python interpreter is running.

## Requirements

- Python 3.9 or newer
- pip

## Install for development

From the project directory, create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell, activate it with:

```powershell
.venv\Scripts\Activate.ps1
```

Install GNG in editable mode:

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

Editable installation makes changes to `src/gng/` available without reinstalling.

## Usage

Run GNG's terminal welcome screen:

```bash
gng
```

Check the Python executable and version GNG is using:

```bash
gng doctor
```

Show command help:

```bash
gng --help
```

## Terminal display

The banner selects a large or compact wordmark based on the available terminal width. In a terminal, it uses color when supported. For non-interactive output, GNG prints a short plain status line instead.

- Set `NO_COLOR` to disable color.
- Set `GNG_ASCII=1` to use an ASCII-compatible banner.
- The banner and palette are implemented in `src/gng/banner.py`.

## Project layout

```text
src/gng/
├── __init__.py
├── __main__.py   # Enables `python -m gng`
├── banner.py     # Wordmark, colors, and terminal rendering
└── cli.py        # Typer application and commands
tests/
└── test_banner.py
```

## Development

Install pytest and run the banner tests:

```bash
python -m pip install pytest
python -m pytest
```

## License

No license has been specified yet.
