"""Small output helpers shared by every command: markers, color and failures."""

import os
import sys

import typer

from gng import banner

# (unicode marker, ASCII fallback). The shape carries the meaning; color is a bonus.
_MARKS = {
    "ok": ("✓", "OK"),
    "warn": ("!", "!!"),
    "fail": ("✗", "XX"),
    "info": ("•", "-"),
}


def _paint(text, code):
    if not banner.color_enabled(sys.stdout):
        return text
    return f"\x1b[{code}m{text}\x1b[0m"


def mark(kind):
    """A one-character status marker for 'ok', 'warn', 'fail' or 'info'."""
    glyph = _MARKS[kind][0 if banner.unicode_ok() else 1]
    pal = banner.palette()
    codes = {
        "ok": "1;" + pal["cyan"],
        "warn": "1;" + pal["magenta"],
        "fail": "1;31",
        "info": pal["gray"],
    }
    return _paint(glyph, codes[kind])


def say(kind, text, indent=2):
    """Print one status line, like '  ✓ python 3.14.0'."""
    print(" " * indent + mark(kind) + " " + text)


def note(text, indent=2):
    """Print a plain indented line."""
    print(" " * indent + text)


def plural(count, word):
    """plural(1, 'file') -> '1 file', plural(2, 'file') -> '2 files'."""
    return f"{count} {word}" + ("" if count == 1 else "s")


def short_path(path):
    """Relative to the current folder when the path is inside it, otherwise absolute."""
    relative = os.path.relpath(path)
    return os.path.abspath(path) if relative.startswith("..") else relative


def die(what, fix, code=1):
    """Print a precise error plus a next step, then stop with a non-zero exit code."""
    banner.error(what, fix)
    raise typer.Exit(code)
