import typer
from gng import banner

app = typer.Typer(add_completion=False, help="GNG // developer toolkit")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        banner.show()          # bare `gng` shows the banner


@app.command()
def doctor():
    """Check your Python setup."""
    import sys
    typer.echo(f"python {sys.version.split()[0]} at {sys.executable}")