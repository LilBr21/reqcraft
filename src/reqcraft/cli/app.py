import typer
from reqcraft.cli.commands.run import run
from reqcraft.cli.commands.import_curl import import_app

app = typer.Typer(help="reqcraft — terminal-first HTTP client and test runner")
app.command(name="run")(run)
app.add_typer(import_app, name="import")

@app.callback()
def callback() -> None:
    pass

def main():
    app()