from pathlib import Path
import typer
from rich.console import Console
from reqcraft.utils.yaml_loader import load_collection, load_environment
from reqcraft.core.executor import execute, execute_dry_run

console = Console()

def run(
    collection: Path = typer.Argument(..., help="Path to collection YAML file"),
    env: Path = typer.Option(None, "--env", help="Path to environment file"),
    var: list[str] = typer.Option([], "--var", help="Override variable (key=value)"),
    only: list[str] = typer.Option([], "--only", help="Collection items to run"),
    skip: list[str] = typer.Option([], "--skip", help="Collection items to skip"),
    fail_fast: bool = typer.Option(False, "--fail-fast", help="Quit running tests after first fail"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Dry run request without making actual api calls"),
):
    try:
        loaded_collection = load_collection(collection)
        variables: dict[str, str] = {}

        if env:
            loaded_env = load_environment(env)
            variables = dict(loaded_env.variables)
    except Exception as e:
        console.print(f"[red]Validation error: {e}[/red]")
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
        console.print(f"[red]Validation error: {e}[/red]")
        raise typer.Exit(code=2)
    except Exception as e:
        console.print(f"[red]Network error: {e}[/red]")
        raise typer.Exit(code=3)

    console.print(f"[bold]Running {loaded_collection.name}[/bold]")
    for result in report.results:
        console.print(f"Status code: {result.status_code}")
        console.print(f"Response time (ms): {result.response_time_ms}")
        console.print(f"Response:")
        console.print_json(result.body)
        icon = "✓" if result.passed else "✗"
        color = "green" if result.passed else "red"
        console.print(f"[{color}]{icon} {result.name} (Test result)[/{color}]")
        for a in result.assertions:
            console.print(f"  {a.message}")
    console.print(f"\n{report.passed}/{report.total} passed")

    if report.failed > 0:
        raise typer.Exit(code=1)
