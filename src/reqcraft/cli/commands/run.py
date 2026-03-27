import sys
from pathlib import Path
import typer
import json
from enum import Enum
from rich.console import Console
from reqcraft.utils.yaml_loader import load_collection, load_environment
from reqcraft.core.executor import execute, execute_dry_run
from reqcraft.core.reporter import print_report

class OutputFormat(str, Enum):
    JSON = "json"
    TEXT = "text"

class ErrorType(str, Enum):
    VALIDATION = "Validation"
    NETWORK = "Network"

console = Console()

def _handle_error(error: Exception, error_type: ErrorType, output_format: OutputFormat):
    if output_format == OutputFormat.JSON:
        print(f"{error_type} error: {error}", file=sys.stderr)
    else:
        console.print(f"[red]{error_type} error: {error}[/red]")

def run(
    collection: Path = typer.Argument(..., help="Path to collection YAML file"),
    env: Path = typer.Option(None, "--env", help="Path to environment file"),
    var: list[str] = typer.Option([], "--var", help="Override variable (key=value)"),
    only: list[str] = typer.Option([], "--only", help="Collection items to run"),
    skip: list[str] = typer.Option([], "--skip", help="Collection items to skip"),
    fail_fast: bool = typer.Option(False, "--fail-fast", help="Quit running tests after first fail"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Dry run request without making actual api calls"),
    verbose: bool = typer.Option(False, "--verbose", help="Verbose output"),
    output: OutputFormat = typer.Option(OutputFormat.TEXT, "--output", help="Result printed as a single JSON object"),
):
    try:
        loaded_collection = load_collection(collection)
        variables: dict[str, str] = {}

        if env:
            loaded_env = load_environment(env)
            variables = dict(loaded_env.variables)
    except Exception as e:
        _handle_error(e, ErrorType.VALIDATION, output)
        raise typer.Exit(code=2)

    for v in var:
        key, value = v.split("=", 1)
        variables[key] = value

    try:
        if dry_run:
            execute_dry_run(loaded_collection, variables)
            return
        report = execute(loaded_collection, variables, only, skip, fail_fast)
    except ValueError as e:
        _handle_error(e, ErrorType.VALIDATION, output)
        raise typer.Exit(code=2)
    except Exception as e:
        _handle_error(e, ErrorType.NETWORK, output)
        raise typer.Exit(code=3)

    if output == OutputFormat.JSON:
        report_dict = report.model_dump()
        for result in report_dict["results"]:
            if result["body"]:
                try:
                    parsed_result = json.loads(result["body"])
                    result["body"] = parsed_result
                except json.JSONDecodeError:
                    pass
        report_json = json.dumps(report_dict, indent=2)
        print(report_json)
    else:
        print_report(report, loaded_collection.name, verbose)

    if report.failed > 0:
        raise typer.Exit(code=1)
