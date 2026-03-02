import typer
from reqcraft.cli.commands import run

app = typer.Typer(help="reqcraft — terminal-first HTTP client and test runner")
app.add_typer(run.app, name="run")

def main():
    app()