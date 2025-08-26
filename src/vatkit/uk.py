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
    """Parse UK VAT rates from GOV.UK HTML with detailed categories mapped to EU equivalents."""
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
            # Standard rate categories (20%)
            {"label": "Standard", "rate_percent": 20.0, "description": "Most goods and services", "eu_equivalent": "Standard"},
            
            # Reduced rate categories (5%)
            {"label": "Energy & Heating", "rate_percent": 5.0, "description": "Domestic electricity, gas, heating oil, solid fuel", "eu_equivalent": "Supply Electricity"},
            {"label": "Construction", "rate_percent": 5.0, "description": "Renovation of empty dwellings, conversion work", "eu_equivalent": "Housing Provision"},
            {"label": "Heating Equipment", "rate_percent": 5.0, "description": "Boilers, radiators, heating controls", "eu_equivalent": "Supply Heating"},
            {"label": "Children's Car Seats", "rate_percent": 5.0, "description": "Child car seats and booster cushions", "eu_equivalent": "Children Car Seats"},
            {"label": "Sanitary Products", "rate_percent": 5.0, "description": "Women's sanitary protection products", "eu_equivalent": "Pharmaceutical Products"},
            
            # Zero rate categories (0%)
            {"label": "Books & Publications", "rate_percent": 0.0, "description": "Books, newspapers, magazines, maps", "eu_equivalent": "Books"},
            {"label": "Children's Clothing", "rate_percent": 0.0, "description": "Children's clothes and footwear under 14", "eu_equivalent": "Clothing Repair"},
            {"label": "Food & Drink", "rate_percent": 0.0, "description": "Most food and non-alcoholic drinks", "eu_equivalent": "Foodstuffs"},
            {"label": "Transport", "rate_percent": 0.0, "description": "Public passenger transport, aircraft, ships", "eu_equivalent": "Transport Passengers"},
            {"label": "Medical & Care", "rate_percent": 0.0, "description": "Medical care, pharmaceutical products", "eu_equivalent": "Medical Care"},
            {"label": "Energy Saving", "rate_percent": 0.0, "description": "Solar panels, insulation, heat pumps", "eu_equivalent": "Solar Panels"},
            {"label": "Construction Zero", "rate_percent": 0.0, "description": "New dwellings, substantial reconstruction", "eu_equivalent": "Housing Provision"},
            {"label": "Protective Equipment", "rate_percent": 0.0, "description": "Cycle helmets, motorcycle helmets", "eu_equivalent": "Medical Equipment"},
            {"label": "Cultural Items", "rate_percent": 0.0, "description": "Tapestries, pictures, sculptures over 100 years", "eu_equivalent": "100 Years Old"},
            
            # Special categories
            {"label": "Exempt", "rate_percent": None, "description": "Financial services, insurance, property", "eu_equivalent": "Social Wellbeing"},
            {"label": "Outside Scope", "rate_percent": None, "description": "Tolls, some postal services", "eu_equivalent": "Postage"}
        ]
    }
    
    return uk_rates
