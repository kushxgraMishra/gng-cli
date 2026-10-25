"""gng clean: remove Python cache folders that are safe to regenerate."""

import os
import shutil
import sys
from pathlib import Path

import typer

from gng import ui

# Only folders Python and its tools rebuild on their own. Nothing else is ever touched.
CACHE_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
# Never even look inside these.
SKIP_DIRS = {".git", ".venv", "venv", "node_modules"}
SHOW_AT_MOST = 10


def find_caches(root):
    """Return the cache folders under root. Symlinks are never followed or removed."""
    found = []
    for folder, dirs, _files in os.walk(root):
        keep = []
        for name in sorted(dirs):
            path = Path(folder) / name
            if name in CACHE_NAMES:
                if not path.is_symlink():
                    found.append(path)
            elif name not in SKIP_DIRS:
                keep.append(name)
        dirs[:] = keep
    return found


def folder_size(path):
    total = 0
    for folder, _dirs, files in os.walk(path):
        for name in files:
            try:
                total += os.path.getsize(os.path.join(folder, name))
            except OSError:
                pass
    return total


def human(size):
    for unit in ("B", "KB", "MB"):
        if size < 1024:
            return f"{size:.0f} B" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


def run(path, yes, dry_run):
    root = Path(path)
    if not root.is_dir():
        ui.die(f"{path} is not a folder", "give a folder, like: gng clean .")

    found = find_caches(root)
    print()
    if not found:
        ui.say("ok", "nothing to clean")
        return

    sizes = [folder_size(p) for p in found]
    ui.say("info", f"found {ui.plural(len(found), 'cache folder')} ({human(sum(sizes))})")
    for p in found[:SHOW_AT_MOST]:
        ui.note(ui.short_path(p), indent=4)
    if len(found) > SHOW_AT_MOST:
        ui.note(f"...and {len(found) - SHOW_AT_MOST} more", indent=4)

    if dry_run:
        ui.say("info", "dry run, nothing was deleted")
        return

    if not yes:
        if not sys.stdin.isatty():
            ui.die("not deleting without confirmation (there is no terminal to ask)",
                   "run again with --yes to delete, or --dry-run to preview")
        if not typer.confirm("  Delete them?", default=False):
            ui.say("info", "cancelled, nothing was deleted")
            return

    removed, freed, failed = 0, 0, 0
    for p, size in zip(found, sizes):
        try:
            shutil.rmtree(p)
        except OSError:
            failed += 1
        else:
            removed += 1
            freed += size
    ui.say("ok", f"removed {ui.plural(removed, 'folder')}, freed {human(freed)}")
    if failed:
        ui.say("warn", f"{ui.plural(failed, 'folder')} could not be removed (permissions?)")
