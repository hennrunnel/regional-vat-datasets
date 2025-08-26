from typing import Dict, Any, List

# CRA GST/HST summary (authoritative):
# https://www.canada.ca/en/revenue-agency/services/tax/businesses/topics/gst-hst/gst-hst-rates.html
# Step 1: Provide GST/HST by province/territory. PST/QST will be added later.

PROVINCE_GST_HST: List[Dict[str, Any]] = [
    {"code": "CA-AB", "name": "Alberta", "type": "GST", "rate": 5.0},
    {"code": "CA-BC", "name": "British Columbia", "type": "GST", "rate": 5.0},
    {"code": "CA-MB", "name": "Manitoba", "type": "GST", "rate": 5.0},
    {"code": "CA-NB", "name": "New Brunswick", "type": "HST", "rate": 15.0},
    {"code": "CA-NL", "name": "Newfoundland and Labrador", "type": "HST", "rate": 15.0},
    {"code": "CA-NS", "name": "Nova Scotia", "type": "HST", "rate": 15.0},
    {"code": "CA-NT", "name": "Northwest Territories", "type": "GST", "rate": 5.0},
    {"code": "CA-NU", "name": "Nunavut", "type": "GST", "rate": 5.0},
    {"code": "CA-ON", "name": "Ontario", "type": "HST", "rate": 13.0},
    {"code": "CA-PE", "name": "Prince Edward Island", "type": "HST", "rate": 15.0},
    {"code": "CA-QC", "name": "Quebec", "type": "GST", "rate": 5.0},  # QST will be added in step 2
    {"code": "CA-SK", "name": "Saskatchewan", "type": "GST", "rate": 5.0},
    {"code": "CA-YT", "name": "Yukon", "type": "GST", "rate": 5.0},
]


def fetch_ca_vat_rates() -> Dict[str, Any]:
    # Static mapping for step 1 (no live fetch).
    return {"provinces": PROVINCE_GST_HST}


def parse_ca(province_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    countries: List[Dict[str, Any]] = []
    for p in province_data:
        countries.append({
            "iso2": p["code"],
            "name": p["name"],
            "categories": [
                {"label": "Standard", "rate_percent": p["rate"]}
            ]
        })
    return {"countries": countries}


