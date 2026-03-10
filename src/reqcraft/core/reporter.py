from __future__ import annotations

import json

from rich.console import Console, Group
from rich.panel import Panel
from rich.rule import Rule
from rich.syntax import Syntax
from rich.text import Text

from reqcraft.models.result import RequestResult, RunReport

console = Console()


def _status_color(status_code: int | None) -> str:
    if status_code is None:
        return "red"
    if status_code < 300:
        return "green"
    if status_code < 400:
        return "cyan"
    if status_code < 500:
        return "yellow"
    return "red"


def _time_color(ms: float | None) -> str:
    if ms is None:
        return "dim"
    if ms < 200:
        return "green"
    if ms < 500:
        return "yellow"
    return "red"


def _build_verbose_panel(result: RequestResult) -> Panel:
    parts: list = []

    parts.append(Text.assemble(
        (result.request_method or "", "bold cyan"),
        "  ",
        (result.request_url or "", "bold white"),
    ))

    if result.request_headers:
        parts.append(Text(""))
        parts.append(Text("Request Headers", style="bold dim"))
        for k, v in result.request_headers.items():
            parts.append(Text.assemble(
                (f"  {k}", "dim cyan"), (": ", "dim"), (v, "dim white")
            ))

    if result.response_headers:
        parts.append(Text(""))
        parts.append(Text("Response Headers", style="bold dim"))
        for k, v in result.response_headers.items():
            parts.append(Text.assemble(
                (f"  {k}", "dim cyan"), (": ", "dim"), (v, "dim white")
            ))

    if result.body:
        parts.append(Text(""))
        parts.append(Text("Body", style="bold dim"))
        try:
            formatted = json.dumps(json.loads(result.body), indent=2)
            parts.append(Syntax(formatted, "json", theme="monokai", background_color="default"))
        except (json.JSONDecodeError, TypeError):
            parts.append(Text(result.body, style="dim"))

    return Panel(
        Group(*parts),
        title="[dim]Details[/dim]",
        border_style="dim",
        padding=(0, 1),
    )


def _build_request_panel(result: RequestResult, verbose: bool) -> Panel:
    border_color = "green" if result.passed else "red"
    title_icon = "✓" if result.passed else "✗"
    title_style = "bold green" if result.passed else "bold red"
    title = Text.assemble((f"{title_icon}  {result.name or result.request_id}", title_style))

    parts: list = []

    status_str = str(result.status_code) if result.status_code is not None else "—"
    time_str = f"{result.response_time_ms:.0f}ms" if result.response_time_ms is not None else "—"
    parts.append(Text.assemble(
        (status_str, f"bold {_status_color(result.status_code)}"),
        ("  •  ", "dim"),
        (time_str, _time_color(result.response_time_ms)),
    ))

    if result.error:
        parts.append(Text(""))
        parts.append(Text.assemble(("⚠  ", "bold yellow"), (result.error, "yellow")))

    if result.assertions:
        parts.append(Text(""))
        for a in result.assertions:
            icon = "✓" if a.passed else "✗"
            style = "green" if a.passed else "red"
            parts.append(Text.assemble((f"{icon}  ", style), (a.message, style)))

    if verbose:
        parts.append(Text(""))
        parts.append(_build_verbose_panel(result))

    return Panel(
        Group(*parts),
        title=title,
        border_style=border_color,
        padding=(0, 1),
    )


def print_report(report: RunReport, collection_name: str, verbose: bool) -> None:
    console.print()
    console.print(f"  [bold white]Running[/bold white] [bold cyan]{collection_name}[/bold cyan]")
    console.print()

    for result in report.results:
        console.print(_build_request_panel(result, verbose))

    summary_color = "green" if report.failed == 0 else "red"
    parts = [
        (str(report.passed), f"bold {summary_color}"),
        ("/", "dim white"),
        (str(report.total), "bold white"),
        (" passed", "white"),
    ]
    if report.skipped:
        parts += [("  •  ", "dim"), (f"{report.skipped} skipped", "bold yellow")]
    if report.failed:
        parts += [("  •  ", "dim"), (f"{report.failed} failed", "bold red")]

    summary = Text.assemble(*parts)
    console.print(Rule(summary, style=summary_color))
    console.print()
