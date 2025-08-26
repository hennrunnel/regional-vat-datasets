from typing import Dict, Any

from rich import print as rprint
from .ch import fetch_ch_vat_rates, parse_ch_html


def fetch_li_vat_rates() -> Dict[str, Any]:
    rprint("[yellow]Liechtenstein mirrors Switzerland (CH) VAT rates. Fetching CH...[/yellow]")
    return fetch_ch_vat_rates()


def parse_li_html(html_content: str) -> Dict[str, Any]:
    ch = parse_ch_html(html_content)
    return {"country": "Liechtenstein", "iso2": "LI", "categories": ch.get("categories", [])}
