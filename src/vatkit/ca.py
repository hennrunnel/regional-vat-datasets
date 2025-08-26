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


# Provincial PST/QST (step 2): add alongside GST for non-HST provinces
PROVINCIAL_TAX = {
    "CA-BC": {"type": "PST", "rate": 7.0},
    "CA-SK": {"type": "PST", "rate": 6.0},
    "CA-MB": {"type": "PST", "rate": 7.0},
    "CA-QC": {"type": "QST", "rate": 9.975},
}


def fetch_ca_vat_rates() -> Dict[str, Any]:
    # Static mapping for step 1 (no live fetch).
    return {"provinces": PROVINCE_GST_HST}


def parse_ca(province_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    countries: List[Dict[str, Any]] = []
    # CRA zero-rated federal supplies (documentation references):
    # - Basic groceries
    # - Prescription drugs
    # - Medical devices
    # - Books
    federal_zero_rated: List[Dict[str, Any]] = [
        {"label": "Basic Groceries", "rate_percent": 0.0},
        {"label": "Prescription Drugs", "rate_percent": 0.0},
        {"label": "Medical Devices", "rate_percent": 0.0},
        {"label": "Books", "rate_percent": 0.0},
    ]
    for p in province_data:
        categories: List[Dict[str, Any]] = []
        # Federal or harmonized tax
        if p["type"] == "HST":
            categories.append({"label": "Standard (HST)", "rate_percent": p["rate"]})
        else:
            categories.append({"label": "Federal (GST)", "rate_percent": p["rate"]})
            prov = PROVINCIAL_TAX.get(p["code"])  # may be None
            if prov:
                label = f"Provincial ({prov['type']})"
                categories.append({"label": label, "rate_percent": prov["rate"]})
        # Add federal zero-rated categories applicable nationwide
        categories.extend(federal_zero_rated)

        countries.append({
            "iso2": p["code"],
            "name": p["name"],
            "categories": categories,
        })
    return {"countries": countries}


