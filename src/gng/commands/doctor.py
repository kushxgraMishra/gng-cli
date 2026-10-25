"""gng doctor: check that your Python setup is ready for development."""

import importlib.util
import os
import shutil
import sys

from gng import banner, ui

MIN_PYTHON = (3, 9)


def real_width():
    """The width the terminal itself reports, or None when output is not a terminal."""
    try:
        return os.get_terminal_size(sys.__stdout__.fileno()).columns
    except (OSError, ValueError, AttributeError):
        return None


# Each check returns (kind, text, fix). kind is 'ok', 'warn', 'fail' or 'info'.
# fix is a next step shown under anything that is not ok, or None.

def python_check():
    v = sys.version_info
    version = f"{v.major}.{v.minor}.{v.micro}"
    if (v.major, v.minor) >= MIN_PYTHON:
        return ("ok", f"python {version}", None)
    return ("fail", f"python {version} is too old (need 3.9 or newer)",
            "install a newer Python from python.org")


def venv_check():
    if sys.prefix != getattr(sys, "base_prefix", sys.prefix):
        return ("ok", f"virtual environment active ({os.path.basename(sys.prefix)})", None)
    return ("warn", "no virtual environment active",
            "python3 -m venv .venv && source .venv/bin/activate")


def pip_check():
    if importlib.util.find_spec("pip"):
        return ("ok", "pip available", None)
    return ("warn", "pip not found", "python3 -m ensurepip --upgrade")


def git_check():
    if shutil.which("git"):
        return ("ok", "git found", None)
    return ("warn", "git not found", "install it from git-scm.com (optional)")


def terminal_check():
    real = real_width()
    env = os.environ.get("COLUMNS", "")
    if env.isdigit() and int(env) > 0:
        if real is not None and int(env) != real:
            return ("warn", f"COLUMNS={env} overrides the real terminal width ({real})",
                    "unset COLUMNS")
        return ("ok", f"terminal width {env} columns", None)
    if real is not None:
        return ("ok", f"terminal width {real} columns", None)
    return ("info", "not a terminal (output is piped), assuming 80 columns", None)


def style_check():
    if os.environ.get("NO_COLOR"):
        colors = "off (NO_COLOR is set)"
    elif not banner.color_enabled(sys.stdout):
        colors = "off (not a color terminal)"
    else:
        colors = banner.color_depth()
    glyphs = "unicode" if banner.unicode_ok() else "ascii"
    return ("info", f"colors: {colors}, characters: {glyphs}", None)


CHECKS = (python_check, venv_check, pip_check, git_check, terminal_check, style_check)


def run():
    """Print every check. Returns 1 if something failed, otherwise 0."""
    results = [check() for check in CHECKS]
    print()
    for kind, text, fix in results:
        ui.say(kind, text)
        if fix:
            ui.note(f"next: {fix}", indent=4)

    fails = sum(1 for kind, _, _ in results if kind == "fail")
    warns = sum(1 for kind, _, _ in results if kind == "warn")
    print()
    if fails:
        ui.say("fail", f"{ui.plural(fails, 'problem')} to fix")
    elif warns:
        ui.say("warn", f"ready, with {ui.plural(warns, 'warning')}")
    else:
        ui.say("ok", "all clear")
    return 1 if fails else 0
