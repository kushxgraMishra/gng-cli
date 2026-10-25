from pathlib import Path

import typer

from gng import banner
from gng.commands import clean as clean_cmd
from gng.commands import doctor as doctor_cmd
from gng.commands import folder as folder_cmd
from gng.commands import filesystem as fs_cmd
from gng.commands import new as new_cmd
from gng.commands import todo as todo_cmd

app = typer.Typer(add_completion=False, help="GNG // developer toolkit")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        banner.show()  # bare `gng` shows the banner


@app.command()
def new(
    name: str = typer.Argument(..., help="Project name, like my-tool"),
    directory: Path = typer.Option(Path("."), "--dir", "-d", help="Folder to create it in"),
):
    """Start a new Python command-line project."""
    new_cmd.run(name, directory)


@app.command()
def folder(
    name: str = typer.Argument(..., help="Name of the folder to create"),
    directory: Path = typer.Option(Path("."), "--dir", "-d", help="Parent folder"),
):
    """Create a folder in the current location or under --dir."""
    folder_cmd.run(name, directory)


@app.command("ls")
def list_folder(path: Path = typer.Argument(Path("."), help="Folder to list")):
    """List files and folders, including hidden entries."""
    fs_cmd.list_entries(path)


@app.command("open")
def open_directory(path: Path = typer.Argument(Path("."), help="Folder to enter")):
    """Change the current terminal directory (requires the zsh integration)."""
    if not path.is_dir():
        typer.echo(f"gng: no such folder: {path}", err=True)
        raise typer.Exit(1)
    typer.echo(
        "Changing the current terminal directory requires the GNG zsh integration. "
        "Load it with: source ~/.zshrc",
        err=True,
    )
    raise typer.Exit(1)


@app.command()
def touch(paths: list[Path] = typer.Argument(..., help="Empty file path(s) to create")):
    """Create one or more empty files without overwriting existing entries."""
    fs_cmd.create_empty(paths)


@app.command("rm")
def remove_files(
    paths: list[Path] = typer.Argument(..., help="File path(s) to delete"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Confirm deletion without prompting"),
):
    """Delete one or more files; folders are not removed."""
    fs_cmd.delete_files(paths, yes)


@app.command("rmdir")
def remove_folder(
    path: Path = typer.Argument(..., help="Folder to delete, including its contents"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Confirm deletion without prompting"),
):
    """Delete a folder and everything inside it."""
    fs_cmd.delete_folder(path, yes)


@app.command()
def rename(
    path: Path = typer.Argument(..., help="File to rename"),
    new_name: str = typer.Argument(..., help="New file name in the same folder"),
):
    """Rename a file without replacing an existing entry."""
    fs_cmd.rename_file(path, new_name)


@app.command()
def doctor():
    """Check that your Python setup is ready."""
    code = doctor_cmd.run()
    if code:
        raise typer.Exit(code)


@app.command()
def todo(
    path: Path = typer.Argument(Path("."), help="Folder or file to scan"),
):
    """List TODO and FIXME notes in your code."""
    todo_cmd.run(path)


@app.command()
def clean(
    path: Path = typer.Argument(Path("."), help="Folder to clean"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Delete without asking"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Only show what would be deleted"),
):
    """Remove Python cache folders (__pycache__, .pytest_cache, ...)."""
    clean_cmd.run(path, yes, dry_run)
