import typer
from reqcraft.cli.commands.run import run

app = typer.Typer(help="reqcraft — terminal-first HTTP client and test runner")
app.command(name="run")(run)

@app.callback()
def callback() -> None:
    pass

def main():
    app()