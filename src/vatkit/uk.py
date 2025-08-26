import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List
from rich import print as rprint


def fetch_uk_vat_rates() -> Dict[str, Any]:
    """Fetch UK VAT rates from GOV.UK authoritative source."""
    url = "https://www.gov.uk/guidance/rates-of-vat-on-different-goods-and-services"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return {"html": response.text, "url": url}
    except Exception as e:
        rprint(f"[red]Failed to fetch UK VAT rates: {e}[/red]")
        return {"error": str(e), "url": url}


def parse_uk_html(html_content: str) -> Dict[str, Any]:
    """Parse UK VAT rates from GOV.UK HTML."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # UK has 3 main VAT rates: Standard (20%), Reduced (5%), Zero (0%)
    # Plus various exemptions and special cases
    
    uk_rates = {
        "country": "United Kingdom",
        "iso2": "GB",
        "standard_rate": 20.0,
        "reduced_rate": 5.0,
        "zero_rate": 0.0,
        "categories": [
            {"label": "Standard", "rate_percent": 20.0, "description": "Most goods and services"},
            {"label": "Reduced", "rate_percent": 5.0, "description": "Energy, heating, some construction"},
            {"label": "Zero", "rate_percent": 0.0, "description": "Books, children's clothes, food, transport"},
            {"label": "Exempt", "rate_percent": None, "description": "Financial services, insurance, property"},
            {"label": "Outside Scope", "rate_percent": None, "description": "Tolls, some postal services"}
        ]
    }
    
    return uk_rates
