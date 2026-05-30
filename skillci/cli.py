from pathlib import Path

import typer
from rich.console import Console

from skillci import __version__
from skillci.compare import run_compare
from skillci.report.json_report import render_json
from skillci.report.markdown_report import render_github_markdown, render_markdown
from skillci.report.terminal_report import (
    render_compare_report,
    render_report,
    render_static_health,
)
from skillci.runner import run_both_test, run_lint, run_llm_test, run_local_test
from skillci.runner_init import run_init
from skillci.runner_snapshot import run_snapshot


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"skillci {__version__}")
        raise typer.Exit()


app = typer.Typer(
    help="SkillCI: test Agent Skills before shipping.",
    invoke_without_command=True,
)


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", "-v", help="Show version and exit.", is_eager=True
    ),
) -> None:
    """SkillCI: test Agent Skills before shipping."""
    version_callback(version)


@app.command()
def init(skill_path: Path) -> None:
    """Create a starter skillci.yaml for a Skill directory."""
    config_path = run_init(skill_path)
    typer.echo(f"Created config: {config_path}")


@app.command()
def lint(skill_path: Path) -> None:
    """Run static health checks for a Skill directory."""
    result = run_lint(skill_path)
    render_static_health(result, Console())
    raise typer.Exit(0 if result.passed else 1)


@app.command()
def snapshot(skill_path: Path) -> None:
    """Save a baseline test report for later regression comparison."""
    snapshot_path = run_snapshot(skill_path)
    typer.echo(f"Saved baseline snapshot: {snapshot_path}")


@app.command()
def test(
    skill_path: Path,
    mode: str = typer.Option("local", help="Trigger test mode: local, llm, or both."),
    json_output: bool = typer.Option(False, "--json", help="Output JSON report."),
    provider: str = typer.Option("openai", help="LLM judge provider. Use mock for tests."),
    compare: str | None = typer.Option(None, help="Compare with baseline."),  # noqa: B008
    no_cache: bool = typer.Option(False, "--no-cache", help="Disable LLM judge cache."),
) -> None:
    """Run Skill trigger tests."""
    if mode == "local":
        report = run_local_test(skill_path)
    elif mode == "llm":
        report = run_llm_test(skill_path, provider_name=provider, use_cache=not no_cache)
    elif mode == "both":
        report = run_both_test(skill_path, provider_name=provider, use_cache=not no_cache)
    else:
        typer.echo(f"Unsupported mode: {mode}. Use local, llm, or both.", err=True)
        raise typer.Exit(2)

    if compare is not None and compare != "latest":
        typer.echo("Only --compare latest is supported in v0.1.", err=True)
        raise typer.Exit(2)

    if compare == "latest":
        baseline_path = Path(".skillci/baselines") / report.skill_name / "latest.json"
        if not baseline_path.exists():
            typer.echo("No baseline snapshot found. Run `skillci snapshot` first.", err=True)
            raise typer.Exit(2)
        regression = run_compare(baseline_path, report)
        if json_output:
            typer.echo(render_json(report))
            render_compare_report(regression, Console())
        else:
            render_report(report, Console())
            render_compare_report(regression, Console())
        raise typer.Exit(0 if report.passed else 1)

    if json_output:
        typer.echo(render_json(report))
    else:
        render_report(report, Console())
    raise typer.Exit(0 if report.passed else 1)


@app.command()
def report(
    skill_path: Path,
    format: str = typer.Option("markdown", help="Report format: markdown or github."),
    output: Path | None = typer.Option(None, help="Optional output file path."),  # noqa: B008
) -> None:
    """Generate a SkillCI report."""
    current_report = run_local_test(skill_path)

    if format == "markdown":
        content = render_markdown(current_report)
    elif format == "github":
        content = render_github_markdown(current_report)
    else:
        typer.echo(f"Unsupported format: {format}. Use markdown or github.", err=True)
        raise typer.Exit(2)

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content, encoding="utf-8")
        typer.echo(f"Wrote report to {output}")
    else:
        typer.echo(content)


if __name__ == "__main__":
    app()
