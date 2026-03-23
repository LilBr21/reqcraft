import sys
import typer
from pathlib import Path
from rich.console import Console
from reqcraft.core.curl_parser import parse_curl, CurlParserError
from reqcraft.core.curl_to_collection import parsed_curl_to_collection, collection_to_yaml

import_app = typer.Typer(help="Import requests from external formats")

console = Console()

@import_app.command(name="curl")
def import_curl(
        curl_command: str | None = typer.Argument(None),
        output: Path | None = typer.Option(None, "--output", "-o", help="Write to file instead of stdout"),
        force: bool = typer.Option(False, "--force", "-f", help="Force overwrite of existing file"),
):
    if curl_command is None:
        if not sys.stdin.isatty():
            curl_command = sys.stdin.read().strip()
        else:
            console.print("[red]Error: provide curl command as argument or pipe it via stdin[/red]")
            raise typer.Exit(code=2)

    try:
        parsed_curl = parse_curl(curl_command)
    except CurlParserError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=2)

    curl_collection = parsed_curl_to_collection(parsed_curl)
    yaml_collection = collection_to_yaml(curl_collection)

    if output is None:
        console.print(yaml_collection)
    else:
        if output.exists() and not force:
            console.print("[red]Error: output file already exists[/red]")
            raise typer.Exit(code=2)
        else:
            output.write_text(yaml_collection)
