from typing import Optional, List, Dict, Any
from rich import print as rprint

from .tedb import fetch_vat_rates
from .mapper import map_tedb_to_unified
from .render import write_json


def run_region(region: str, *, date_from: str, date_to: str, states: Optional[List[str]]) -> Optional[Dict[str, Any]]:
    region = (region or "").lower()
    if region == "eu":
        rprint(f"[bold]Fetching[/bold] EU (TEDB) VAT rates from {date_from} to {date_to} ...")
        tedb_doc = fetch_vat_rates(date_from=date_from, date_to=date_to, iso_list=states)
        rprint("[bold]Mapping[/bold] EU to unified model ...")
        unified = map_tedb_to_unified(tedb_doc)
        rprint("[bold]Writing[/bold] EU outputs ...")
        write_json(unified, region="eu")
        return unified

    # Placeholder adapters for upcoming regions
    if region in {"uk", "ch", "no", "is", "ca"}:
        rprint(f"[yellow]Region '{region.upper()}' adapter is not implemented yet. Skipping.[/yellow]")
        return None

    rprint(f"[yellow]Unknown region '{region}'. Skipping.[/yellow]")
    return None


