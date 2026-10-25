"""Small, cautious file and folder operations for the GNG CLI."""

import shutil
import sys
from pathlib import Path

import typer

from gng import ui


def list_entries(path):
    """List every direct entry in a folder, including hidden entries."""
    folder = Path(path)
    if not folder.is_dir():
        ui.die(f"{path} is not an existing folder", "give a folder, like: gng ls .")

    try:
        entries = sorted(folder.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower()))
    except OSError as error:
        ui.die(f"could not read {ui.short_path(folder)}: {error.strerror or error}",
               "check that you have permission to read the folder")

    if not entries:
        ui.say("info", f"{ui.short_path(folder)} is empty")
        return

    ui.say("info", f"{len(entries)} entries in {ui.short_path(folder)}")
    for entry in entries:
        suffix = "/" if entry.is_dir() and not entry.is_symlink() else ""
        ui.note(entry.name + suffix, indent=4)


def create_empty(paths):
    """Create one or more empty files without overwriting existing entries."""
    targets = [Path(path) for path in paths]
    for target in targets:
        if target.exists() or target.is_symlink():
            ui.die(f"{ui.short_path(target)} already exists", "choose a different file name")
        if not target.parent.is_dir():
            ui.die(f"parent folder for {ui.short_path(target)} does not exist",
                   "create the parent folder first")

    created = []
    try:
        for target in targets:
            with target.open("x", encoding="utf-8"):
                pass
            created.append(target)
    except OSError as error:
        for target in created:
            target.unlink(missing_ok=True)
        ui.die(f"could not create {ui.short_path(target)}: {error.strerror or error}",
               "check that you can write to the parent folder")

    ui.say("ok", f"created {ui.plural(len(created), 'empty file')}")
    for target in created:
        ui.note(ui.short_path(target), indent=4)


def _confirm_delete(description, yes):
    if yes:
        return
    if not sys.stdin.isatty():
        ui.die("not deleting without confirmation (there is no terminal to ask)",
               "run again with --yes to confirm")
    if not typer.confirm(f"  Delete {description}?", default=False):
        ui.say("info", "cancelled, nothing was deleted")
        raise typer.Exit()


def delete_files(paths, yes=False):
    """Delete files only; directories are never removed by this command."""
    targets = [Path(path) for path in paths]
    for target in targets:
        if not target.exists() and not target.is_symlink():
            ui.die(f"{ui.short_path(target)} does not exist", "check the file path")
        if target.is_dir() and not target.is_symlink():
            ui.die(f"{ui.short_path(target)} is a folder", "use gng rmdir for folders")

    _confirm_delete(f"{ui.plural(len(targets), 'file')} ({', '.join(ui.short_path(p) for p in targets)})", yes)
    deleted = 0
    for target in targets:
        try:
            target.unlink()
            deleted += 1
        except OSError as error:
            ui.die(f"could not delete {ui.short_path(target)}: {error.strerror or error}",
                   "check that you can write to the parent folder")
    ui.say("ok", f"deleted {ui.plural(deleted, 'file')}")


def _protected_folder(target):
    resolved = target.resolve()
    cwd = Path.cwd().resolve()
    home = Path.home().resolve()
    if resolved == Path(resolved.anchor) or resolved == home or resolved in home.parents:
        return True
    return resolved == cwd or resolved in cwd.parents


def delete_folder(path, yes=False):
    """Recursively delete one folder after confirmation; never follow a symlink."""
    target = Path(path)
    if target.is_symlink():
        ui.die(f"{ui.short_path(target)} is a symbolic link",
               "choose the actual folder path; symbolic links are not removed")
    if not target.is_dir():
        ui.die(f"{ui.short_path(target)} is not an existing folder", "check the folder path")
    if _protected_folder(target):
        ui.die(f"refusing to delete protected folder {ui.short_path(target)}",
               "choose a folder below your current location")

    _confirm_delete(f"folder {ui.short_path(target)} and everything inside it", yes)
    try:
        shutil.rmtree(target)
    except OSError as error:
        ui.die(f"could not delete {ui.short_path(target)}: {error.strerror or error}",
               "check that you can write to the folder and its contents")
    ui.say("ok", f"deleted folder {ui.short_path(target)}/")


def rename_file(path, new_name):
    """Rename a file in place without replacing another entry."""
    source = Path(path)
    if not source.exists() and not source.is_symlink():
        ui.die(f"{ui.short_path(source)} does not exist", "check the file path")
    if source.is_dir() and not source.is_symlink():
        ui.die(f"{ui.short_path(source)} is a folder", "rename files with this command")
    if new_name in {".", ".."} or Path(new_name).name != new_name or Path(new_name).is_absolute():
        ui.die(f"'{new_name}' is not a file name", "give only the new name, like: report-old.txt")

    destination = source.with_name(new_name)
    if destination.exists() or destination.is_symlink():
        ui.die(f"{ui.short_path(destination)} already exists", "choose another file name")
    try:
        source.rename(destination)
    except OSError as error:
        ui.die(f"could not rename {ui.short_path(source)}: {error.strerror or error}",
               "check that you can write to the parent folder")
    ui.say("ok", f"renamed {ui.short_path(source)} to {new_name}")
