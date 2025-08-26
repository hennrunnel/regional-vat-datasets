import re
from typing import Dict, Any, List

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from rich import print as rprint

# RSK (Iceland Revenue and Customs) VAT rates page (English)
IS_URL = "https://www.rsk.is/english/companies/value-added-tax/vat-rates/"


def fetch_is_vat_rates() -> Dict[str, Any]:
    try:
        session = requests.Session()
        retries = Retry(total=2, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        resp = session.get(IS_URL, timeout=30)
        resp.raise_for_status()
        return {"html": resp.text, "url": IS_URL}
    except Exception as e:
        rprint(f"[yellow]IS fetch failed, will use fallback: {e}[/yellow]")
        return {"error": str(e), "url": IS_URL}


def parse_is_html(html_content: str) -> Dict[str, Any]:
    """Parse Iceland VAT rates. Fallback to known official rates if parsing fails.
    Target mapping:
      - Standard ~ 24%
      - Reduced ~ 11% (Foodstuffs, Books, Accommodation)
    """
    standard = None
    reduced = None

    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text("\n", strip=True)
        text_norm = re.sub(r"\s+", " ", text).lower()

        # Extract percentage values
        vals = []
        for m in re.finditer(r"(\d{1,2})(?:[\.,](\d))?\s*%", text_norm):
            try:
                val = float(m.group(1) + ("." + m.group(2) if m.group(2) else ".0"))
            except Exception:
                continue
            if 0.0 < val < 30.0:
                vals.append(val)
        uniq = sorted(set(vals))
        if uniq:
            standard = max(uniq)
            reduced_candidates = [v for v in uniq if v <= 15.0]
            if reduced_candidates:
                reduced = max(reduced_candidates)

    # Fallbacks
    if standard is None:
        standard = 24.0
    if reduced is None:
        reduced = 11.0

    categories: List[Dict[str, Any]] = [
        {"label": "Standard", "rate_percent": standard},
        {"label": "Foodstuffs", "rate_percent": reduced},
        {"label": "Books", "rate_percent": reduced},
        {"label": "Accommodation", "rate_percent": reduced},
    ]

    return {"country": "Iceland", "iso2": "IS", "categories": categories}


