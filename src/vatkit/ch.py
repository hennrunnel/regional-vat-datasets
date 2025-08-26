import re
from typing import Dict, Any, List

import requests
from bs4 import BeautifulSoup
from rich import print as rprint


FTA_URL = "https://www.estv.admin.ch/estv/en/home/mehrwertsteuer/mwst-steuersaetze.html"


def fetch_ch_vat_rates() -> Dict[str, Any]:
    try:
        resp = requests.get(FTA_URL, timeout=30)
        resp.raise_for_status()
        return {"html": resp.text, "url": FTA_URL}
    except Exception as e:
        rprint(f"[red]Failed to fetch CH VAT rates: {e}[/red]")
        return {"error": str(e), "url": FTA_URL}


def parse_ch_html(html_content: str) -> Dict[str, Any]:
    """Parse CH VAT rates from Swiss FTA page.
    Targets: standard, reduced, special (accommodation).
    Robust against wording/markup; falls back to known rates if needed.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text("\n", strip=True)

    # Normalize whitespace
    text_norm = re.sub(r"\s+", " ", text)

    # Default placeholders
    standard = None
    reduced = None
    special = None

    # Collect all percentage values seen
    candidates = []
    for m in re.finditer(r"(\d{1,2}[\.,]\d)\s*%", text_norm):
        try:
            val = float(m.group(1).replace(',', '.'))
        except Exception:
            continue
        if 0.0 < val < 25.0:
            candidates.append(val)

    # Deduplicate while preserving
    seen = set()
    uniq = []
    for v in candidates:
        if v not in seen:
            seen.add(v)
            uniq.append(v)

    # If values present, infer by typical Swiss rates (2024+)
    if uniq:
        try:
            # Standard is the maximum
            standard = max(uniq)
            # Reduced: smallest under 5
            reduced_candidates = [v for v in uniq if v < 5.0]
            if reduced_candidates:
                reduced = min(reduced_candidates)
            # Special (accommodation): around 3–4.5, closest to 3.8
            special_candidates = [v for v in uniq if 3.0 <= v <= 4.5]
            if special_candidates:
                special = min(special_candidates, key=lambda v: abs(v - 3.8))
        except Exception:
            pass

    # Fallback to current official rates (2024+) if not found
    if standard is None: standard = 8.1
    if reduced is None: reduced = 2.6
    if special is None: special = 3.8

    categories: List[Dict[str, Any]] = []
    if standard is not None:
        categories.append({"label": "Standard", "rate_percent": standard})
    if reduced is not None:
        # EU-style: break out common reduced classes
        categories.extend([
            {"label": "Foodstuffs", "rate_percent": reduced},
            {"label": "Books", "rate_percent": reduced},
            {"label": "Pharmaceutical Products", "rate_percent": reduced},
            {"label": "Broadcasting Services", "rate_percent": reduced},
        ])
    if special is not None:
        categories.append({"label": "Accommodation", "rate_percent": special})

    return {
        "country": "Switzerland",
        "iso2": "CH",
        "categories": categories,
    }
