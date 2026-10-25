"""Create a single folder without overwriting existing files or directories."""

from pathlib import Path

from gng import ui


def run(name, directory):
    if name in {".", ".."} or Path(name).name != name or Path(name).is_absolute():
        ui.die(
            f"'{name}' is not a folder name",
            "use one folder name, like: gng folder notes",
        )

    parent = Path(directory)
    if not parent.is_dir():
        ui.die(
            f"{directory} is not an existing folder",
            "choose an existing parent folder with --dir",
        )

    target = parent / name
    if target.exists():
        ui.die(f"{ui.short_path(target)} already exists", "choose another folder name")

    try:
        target.mkdir()
    except OSError as error:
        ui.die(
            f"could not create {ui.short_path(target)}: {error.strerror or error}",
            "check that you can write to the parent folder",
        )

    ui.say("ok", f"created {ui.short_path(target)}/")
