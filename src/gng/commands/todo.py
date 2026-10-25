"""gng todo: list TODO / FIXME style notes left in code comments."""

import os
import re
from pathlib import Path

from gng import ui

# A note is a comment marker followed by a tag word (TODO, FIXME, HACK or XXX).
NOTE = re.compile(r"(?:#|//|/\*|<!--)\s*(TODO|FIXME|HACK|XXX)\b:?\s*(.*)")

CODE_SUFFIXES = {
    ".py", ".sh", ".js", ".ts", ".java", ".c", ".h", ".cpp", ".go", ".rs",
    ".html", ".css", ".toml", ".yml", ".yaml",
}
SKIP_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", "dist", "build",
}
MAX_BYTES = 1_000_000  # skip huge files


def code_files(root):
    """Yield the files worth scanning under root (or root itself if it is a file)."""
    if root.is_file():
        yield root
        return
    for folder, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs
                         if d not in SKIP_DIRS and not d.endswith(".egg-info"))
        for name in sorted(files):
            path = Path(folder) / name
            if path.suffix in CODE_SUFFIXES:
                yield path


def find_notes(root):
    """Return a list of (path, line number, tag, message)."""
    notes = []
    for path in code_files(root):
        try:
            if path.stat().st_size > MAX_BYTES:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for number, line in enumerate(text.splitlines(), start=1):
            match = NOTE.search(line)
            if match:
                message = re.sub(r"\s*(\*/|-->)\s*$", "", match.group(2)).strip()
                notes.append((path, number, match.group(1), message))
    return notes


def run(path):
    root = Path(path)
    if not root.exists():
        ui.die(f"{path} does not exist", "give a folder or file, like: gng todo .")

    notes = find_notes(root)
    print()
    if not notes:
        ui.say("ok", "no notes found")
        return

    for file, number, tag, message in notes:
        ui.note(f"{ui.short_path(file)}:{number}  {tag}  {message}")
    files = {file for file, _, _, _ in notes}
    print()
    ui.say("info", f"{ui.plural(len(notes), 'note')} in {ui.plural(len(files), 'file')}")
