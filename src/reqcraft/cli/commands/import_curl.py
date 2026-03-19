import typer

import_app = typer.Typer(help="Import requests from external formats")

@import_app.command(name="curl")
def import_curl(curl_command: str | None = typer.Argument(None)):
    print(curl_command)
