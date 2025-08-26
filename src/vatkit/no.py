import re
from typing import Dict, Any, List

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from rich import print as rprint

NO_URL = "https://www.skatteetaten.no/en/business-and-organisation/vat/rates-and-registration/vat-rates/"


def fetch_no_vat_rates() -> Dict[str, Any]:
    try:
        session = requests.Session()
        retries = Retry(total=2, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        resp = session.get(NO_URL, timeout=30)
        resp.raise_for_status()
        return {"html": resp.text, "url": NO_URL}
    except Exception as e:
        rprint(f"[red]Failed to fetch NO VAT rates: {e}[/red]")
        return {"error": str(e), "url": NO_URL}


def parse_no_html(html_content: str) -> Dict[str, Any]:
    """Parse Norway VAT rates from Skatteetaten.
    Target: standard, reduced (food), low rate (transport/culture/accommodation).
    Fallback to known current rates if keywords not found.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text("\n", strip=True)
    text_norm = re.sub(r"\s+", " ", text).lower()

    standard = None
    food = None
    low = None

    # Collect percentages in text
    percents = []
    for m in re.finditer(r"(\d{1,2})(?:[\.,](\d))?\s*%", text_norm):
        val = float(m.group(1) + ("." + m.group(2) if m.group(2) else ".0"))
        if 0.0 < val < 30.0:
            percents.append((val, m.start()))

    # Assign by nearby keywords
    for val, pos in percents:
        window = text_norm[max(0, pos - 100): pos + 60]
        if any(k in window for k in ["standard rate", "ordinary rate", "standard"]):
            standard = val if standard is None else standard
        if any(k in window for k in ["food", "foodstuffs"]):
            food = val if food is None else food
        if any(k in window for k in ["public transport", "passenger transport", "accommodation", "hotel", "culture", "cinema", "sports", "low rate"]):
            low = val if low is None else low

    # If still missing, infer typical NO rates from observed values
    vals = sorted(set(v for v, _ in percents))
    if vals:
        if standard is None:
            standard = max(vals)
        if food is None:
            candidates = [v for v in vals if 10.0 <= v <= 17.0]
            if candidates:
                # closest to 15
                food = min(candidates, key=lambda v: abs(v - 15.0))
        if low is None:
            candidates = [v for v in vals if 8.0 <= v <= 14.0]
            if candidates:
                # closest to 12
                low = min(candidates, key=lambda v: abs(v - 12.0))

    # Final fallback to known rates if nothing found
    if standard is None: standard = 25.0
    if food is None: food = 15.0
    if low is None: low = 12.0

    # Map to EU-style categories
    categories: List[Dict[str, Any]] = [
        {"label": "Standard", "rate_percent": standard},
        {"label": "Foodstuffs", "rate_percent": food},
        {"label": "Passenger Transport", "rate_percent": low},
        {"label": "Accommodation", "rate_percent": low},
        {"label": "Cultural Events", "rate_percent": low},
    ]

    return {
        "country": "Norway",
        "iso2": "NO",
        "categories": categories,
    }
