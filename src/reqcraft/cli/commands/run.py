from pathlib import Path
import typer
from rich.console import Console
from reqcraft.utils.yaml_loader import load_collection, load_environment
from reqcraft.core.executor import execute

console = Console()

def run(
    collection: Path = typer.Argument(..., help="Path to collection YAML file"),
    env: Path = typer.Option(None, "--env", help="Path to environment file"),
    var: list[str] = typer.Option([], "--var", help="Override variable (key=value)"),
):
    loaded_collection = load_collection(collection)
    variables: dict[str, str] = {}

    if env:
        loaded_env = load_environment(env)
        variables = dict(loaded_env.variables)

    for v in var:
        key, value = v.split("=", 1)
        variables[key] = value

    report = execute(loaded_collection, variables)

    console.print(f"[bold]Running {loaded_collection.name}[/bold]")
    for result in report.results:
        icon = "✓" if result.passed else "✗"
        color = "green" if result.passed else "red"
        console.print(f"[{color}]{icon} {result.name}[/{color}]")
        for a in result.assertions:
            console.print(f"  {a.message}")
    console.print(f"\n{report.passed}/{report.total} passed")
