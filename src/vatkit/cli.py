from datetime import date
from pathlib import Path
from typing import Optional, List

import typer
from rich import print as rprint

from .adapters import run_region
from .render import write_markdown


app = typer.Typer(add_completion=False, help="Sync EU VAT dataset from TEDB and write JSON + Markdown.")


@app.command()
def sync(
    date_from: Optional[str] = typer.Option(None, "--from", help="From date YYYY-MM-DD (default 2020-01-01)"),
    date_to: Optional[str] = typer.Option(None, "--to", help="To date YYYY-MM-DD (default: today)"),
    states: Optional[str] = typer.Option(None, "--states", help="Comma-separated ISO2 for EU smoke test"),
    regions: Optional[str] = typer.Option("eu", "--regions", help="Comma-separated regions to sync (default: eu)"),
) -> None:
    """Fetch per region → map → write region-scoped JSON and update README grouped by region."""
    if not date_from:
        date_from = "2020-01-01"
    if not date_to:
        date_to = date.today().isoformat()

    if states:
        iso_list: Optional[List[str]] = [s.strip().upper() for s in states.split(',') if s.strip()]
    else:
        iso_list = None

    selected_regions = [r.strip().lower() for r in (regions or 'eu').split(',') if r.strip()]
    last_unified = None
    for region in selected_regions:
        last_unified = run_region(region, date_from=date_from, date_to=date_to, states=iso_list)

    # Render README with region list (EU populated; others stubs)
    write_markdown(last_unified or {"countries": []}, selected_regions)
    rprint("Done.")


if __name__ == "__main__":
    app()


