"""CLI entry point for p2e-character-one-pager."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from .parse import parse
from .profile import classify
from .render import render


@click.group()
def main() -> None:
    """Pathbuilder 2e → single-page HTML character sheet."""
    pass


@main.command()
@click.argument("json_file", type=click.Path(exists=True, dir_okay=False))
@click.option("--out", "-o", default=None, help="Output HTML file path")
@click.option("--page-size", type=click.Choice(["letter", "a4"]), default="letter")
@click.option("--theme", type=click.Choice(["default", "dark"]), default="default")
@click.option("--profile", "profile_override", type=click.Choice(["auto", "caster", "martial", "hybrid"]), default="auto")
@click.option("--skills", "max_skills", type=int, default=8, help="Number of skills to display")
@click.option("--include-prepared/--no-include-prepared", default=True)
@click.option("--include-known/--no-include-known", default=False)
@click.option("--font-source", type=click.Choice(["google", "none"]), default="google")
@click.option("--debug", is_flag=True, default=False, help="Dump computed model as JSON")
def build(
    json_file: str,
    out: str | None,
    page_size: str,
    theme: str,
    profile_override: str,
    max_skills: int,
    include_prepared: bool,
    include_known: bool,
    font_source: str,
    debug: bool,
) -> None:
    """Build a one-pager HTML from a Pathbuilder JSON export."""
    try:
        char = parse(json_file)
    except (json.JSONDecodeError, KeyError) as e:
        click.echo(f"Error parsing {json_file}: {e}", err=True)
        sys.exit(1)

    profile = classify(char, override=profile_override)

    if out is None:
        stem = Path(json_file).stem
        out = f"{stem}_onepager.html"

    html = render(
        char=char,
        profile=profile,
        page_size=page_size,
        theme=theme,
        font_source=font_source,
        max_skills=max_skills,
        include_prepared=include_prepared,
        include_known=include_known,
    )

    Path(out).write_text(html, encoding="utf-8")
    click.echo(f"Profile: {profile.profile_type}")
    click.echo(f"Written: {out}")

    if debug:
        debug_path = Path(out).with_suffix(".debug.json")
        debug_path.write_text(char.model_dump_json(indent=2), encoding="utf-8")
        click.echo(f"Debug: {debug_path}")


if __name__ == "__main__":
    main()
