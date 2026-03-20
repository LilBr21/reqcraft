import sys
import typer
from rich.console import Console
from reqcraft.core.curl_parser import parse_curl, CurlParserError
from reqcraft.core.curl_to_collection import parsed_curl_to_collection, collection_to_yaml

import_app = typer.Typer(help="Import requests from external formats")

console = Console()

@import_app.command(name="curl")
def import_curl(curl_command: str | None = typer.Argument(None)):
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
    console.print(yaml_collection)
