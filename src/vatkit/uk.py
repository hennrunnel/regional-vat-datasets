import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Tuple
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


def _derive_group_and_short(label: str, rate_type: str) -> Tuple[str, str]:
    text = (label or "").lower()
    group = "Other"
    short = label
    # Order matters: match broader sections first
    if "charit" in text:
        group = "Charities"
    elif any(k in text for k in ["electricity", "gas", "heating", "fuel", "water", "sewer", "utilities"]):
        group = "Energy & Utilities"
    elif any(k in text for k in ["energy-saving", "insulation", "solar", "heat pump", "renewable"]):
        group = "Energy-saving Materials"
    elif "building" in text or "construction" in text or "dwelling" in text or "residential" in text:
        group = "Building & Construction"
    elif "land" in text or "property" in text or "leasehold" in text or "freehold" in text:
        group = "Land & Property"
    elif any(k in text for k in ["passenger", "transport"]):
        group = "Passenger Transport"
    elif "freight" in text:
        group = "Freight"
    elif any(k in text for k in ["aircraft", "helicopter", "ship", "boat", "shipbuilding"]):
        group = "Aviation & Shipping"
    elif any(k in text for k in ["book", "magazine", "newspaper", "publication", "leaflet", "pamphlet", "printing", "postage"]):
        group = "Publications & Postage"
    elif any(k in text for k in ["clothes", "footwear", "babywear", "helmet", "protective", "car seat"]):
        group = "Clothing & Protective"
    elif any(k in text for k in ["medical", "pharmac", "prescription", "disabled", "incontinence", "equipment"]):
        group = "Medical & Care"
    elif any(k in text for k in ["finance", "credit", "security", "investment"]):
        group = "Financial Services"
    elif "insurance" in text:
        group = "Insurance"
    # Prefer concise short names per group
    if group == "Charities":
        short = "Charities"
    elif group == "Energy & Utilities":
        short = "Energy (domestic)"
    elif group == "Energy-saving Materials":
        short = "Energy-saving materials"
    elif group == "Building & Construction":
        short = "Building & construction"
    elif group == "Land & Property":
        short = "Land & property"
    elif group == "Passenger Transport":
        short = "Passenger transport"
    elif group == "Freight":
        short = "Freight"
    elif group == "Aviation & Shipping":
        short = "Aviation & shipping"
    elif group == "Publications & Postage":
        short = "Publications & postage"
    elif group == "Clothing & Protective":
        short = "Clothing & protective"
    elif group == "Medical & Care":
        short = "Medical & care"
    elif group == "Financial Services":
        short = "Financial services"
    elif group == "Insurance":
        short = "Insurance"
    elif rate_type == "Standard":
        group = "Standard"
        short = "Standard"
    return group, short


def parse_uk_html(html_content: str) -> Dict[str, Any]:
    """Parse ALL UK VAT rates from GOV.UK HTML - comprehensive extraction from all tables."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all tables
    tables = soup.find_all('table')
    rprint(f"[blue]Found {len(tables)} tables on GOV.UK[/blue]")
    
    all_categories: List[Dict[str, Any]] = []
    
    # UK VAT works by EXCEPTION - everything not listed is Standard rate (20%)
    # Add Standard rate as the first category
    std_group, std_short = _derive_group_and_short("Standard Rate (Default)", "Standard")
    all_categories.append({
        "label": "Standard Rate (Default)",
        "label_short": std_short,
        "group": std_group,
        "rate_percent": 20.0,
        "rate_type": "Standard",
        "reference": "Default UK VAT rate",
        "table_source": "UK VAT System",
        "description": "All goods and services not specifically listed below"
    })
    
    for table_idx, table in enumerate(tables):
        rows = table.find_all('tr')
        if len(rows) < 2:  # Skip tables with just headers
            continue
            
        # Skip header row, process data rows
        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                category_name = cells[0].get_text(strip=True)
                rate_text = cells[1].get_text(strip=True)
                
                # Parse rate
                rate_percent = None
                rate_type = "Unknown"
                
                if "0%" in rate_text:
                    rate_percent = 0.0
                    rate_type = "Zero"
                elif "5%" in rate_text:
                    rate_percent = 5.0
                    rate_type = "Reduced"
                elif "20%" in rate_text:
                    rate_percent = 20.0
                    rate_type = "Standard"
                elif "Exempt" in rate_text:
                    rate_type = "Exempt"
                elif "Outside the scope" in rate_text:
                    rate_type = "Outside Scope"
                elif "The same rate as" in rate_text:
                    rate_type = "Variable"
                
                # Clean up category name
                category_name = category_name.replace('\n', ' ').strip()
                if len(category_name) > 160:  # Truncate very long names for readability
                    category_name = category_name[:157] + "..."
                
                # Get reference info if available
                reference = ""
                if len(cells) >= 3:
                    ref_cell = cells[2].get_text(strip=True)
                    if "VAT Notice" in ref_cell or "Notice" in ref_cell:
                        reference = ref_cell
                
                group, short = _derive_group_and_short(category_name, rate_type)
                category = {
                    "label": category_name,
                    "label_short": short,
                    "group": group,
                    "rate_percent": rate_percent,
                    "rate_type": rate_type,
                    "reference": reference,
                    "table_source": f"Table {table_idx + 1}"
                }
                
                all_categories.append(category)
    
    rprint(f"[blue]Extracted {len(all_categories)} VAT categories from GOV.UK (including Standard rate default)[/blue]")
    
    # Group by rate type for summary
    rate_summary: Dict[str, List[str]] = {}
    for cat in all_categories:
        rate_type = cat["rate_type"]
        rate_summary.setdefault(rate_type, []).append(cat["label_short"])  # summarize by short labels
    
    uk_rates = {
        "country": "United Kingdom",
        "iso2": "GB",
        "total_categories": len(all_categories),
        "rate_summary": rate_summary,
        "categories": all_categories,
        "note": "UK VAT works by exception - Standard rate (20%) applies to all goods/services not specifically listed below"
    }
    
    return uk_rates
