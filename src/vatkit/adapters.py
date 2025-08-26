from typing import Optional, List, Dict, Any
from rich import print as rprint

from .tedb import fetch_vat_rates
from .mapper import map_tedb_to_unified
from .uk import fetch_uk_vat_rates, parse_uk_html
from .ch import fetch_ch_vat_rates, parse_ch_html
from .no import fetch_no_vat_rates, parse_no_html
from .iceland import fetch_is_vat_rates, parse_is_html
from .li import fetch_li_vat_rates, parse_li_html
from .ca import fetch_ca_vat_rates, parse_ca
from .render import write_json


def run_region(region: str, *, date_from: str, date_to: str, states: Optional[List[str]]) -> Optional[Dict[str, Any]]:
    region = (region or "").lower()
    if region == "eu":
        rprint(f"[bold]Fetching[/bold] EU (TEDB) VAT rates from {date_from} to {date_to} ...")
        # Fetch a recent 90-day window up to today, then select latest per category (no strict TODAY filter)
        from datetime import datetime, timedelta
        try:
            today = datetime.fromisoformat(date_to).date()
        except Exception:
            from datetime import date as _d
            today = _d.today()
        window_start = (today - timedelta(days=90)).isoformat()
        tedb_doc = fetch_vat_rates(date_from=window_start, date_to=today.isoformat(), iso_list=states)
        rprint("[bold]Mapping[/bold] EU to unified model (latest per category) ...")
        unified = map_tedb_to_unified(tedb_doc)
        rprint("[bold]Writing[/bold] EU outputs ...")
        write_json(unified, region="eu")
        return unified

    if region == "uk":
        rprint(f"[bold]Fetching[/bold] UK VAT rates from GOV.UK ...")
        uk_data = fetch_uk_vat_rates()
        if "error" in uk_data:
            rprint(f"[red]UK fetch failed: {uk_data['error']}[/red]")
            return None
        
        rprint("[bold]Parsing[/bold] UK HTML to unified model ...")
        uk_rates = parse_uk_html(uk_data["html"])
        
        # Merge UK categories by (group, rate_percent) and ensure distinct names per rate
        detailed = [c for c in uk_rates["categories"] if c.get("rate_percent") is not None]
        merged_map = {}
        def rate_str(v: float) -> str:
            try:
                fv = float(v)
                return f"{int(fv)}%" if abs(fv - int(fv)) < 1e-9 else f"{fv}%"
            except Exception:
                return str(v)
        for c in detailed:
            group = (c.get("group") or c.get("label_short") or c.get("label") or "Category").strip()
            rate = c.get("rate_percent")
            key = (group, rate)
            if key not in merged_map:
                merged_map[key] = {
                    "label": f"{group} ({rate_str(rate)})",
                    "label_short": f"{group} ({rate_str(rate)})",
                    "group": group,
                    "rate_percent": rate,
                    "rate_type": c.get("rate_type"),
                }
        merged = sorted(merged_map.values(), key=lambda x: (x.get("group", ""), x.get("rate_percent", 0)))

        unified = {
            "countries": [{
                "iso2": uk_rates["iso2"],
                "name": uk_rates["country"],
                "categories": merged,
            }]
        }
        
        rprint("[bold]Writing[/bold] UK outputs ...")
        write_json(unified, region="uk")
        return unified

    # Placeholder adapters for upcoming regions
    if region == "ch":
        rprint(f"[bold]Fetching[/bold] CH VAT rates from FTA ...")
        ch_data = fetch_ch_vat_rates()
        if "error" in ch_data:
            rprint(f"[red]CH fetch failed: {ch_data['error']}[/red]")
            return None
        rprint("[bold]Parsing[/bold] CH HTML to unified model ...")
        ch_rates = parse_ch_html(ch_data["html"])
        unified = {
            "countries": [{
                "iso2": ch_rates["iso2"],
                "name": ch_rates["country"],
                "categories": ch_rates["categories"],
            }]
        }
        rprint("[bold]Writing[/bold] CH outputs ...")
        write_json(unified, region="ch")
        return unified

    if region == "no":
        rprint(f"[bold]Fetching[/bold] NO VAT rates from Skatteetaten ...")
        no_data = fetch_no_vat_rates()
        fallback_used = False
        if "error" in no_data:
            rprint(f"[yellow]NO fetch failed, using fallback mapping: {no_data['error']}[/yellow]")
            html = ""
            fallback_used = True
        else:
            html = no_data["html"]
        rprint("[bold]Parsing[/bold] NO HTML to unified model ...")
        no_rates = parse_no_html(html)
        unified = {
            "countries": [{
                "iso2": no_rates["iso2"],
                "name": no_rates["country"],
                "categories": no_rates["categories"],
            }],
            "metadata": {"fallback_used": fallback_used, "source": "Skatteetaten"},
        }
        rprint("[bold]Writing[/bold] NO outputs ...")
        write_json(unified, region="no")
        return unified

    if region == "is":
        rprint(f"[bold]Fetching[/bold] IS VAT rates from RSK ...")
        is_data = fetch_is_vat_rates()
        fallback_used = False
        if "error" in is_data:
            rprint(f"[yellow]IS fetch failed, using fallback mapping: {is_data['error']}[/yellow]")
            html = ""
            fallback_used = True
        else:
            html = is_data["html"]
        rprint("[bold]Parsing[/bold] IS HTML to unified model ...")
        is_rates = parse_is_html(html)
        unified = {
            "countries": [{
                "iso2": is_rates["iso2"],
                "name": is_rates["country"],
                "categories": is_rates["categories"],
            }],
            "metadata": {"fallback_used": fallback_used, "source": "RSK"},
        }
        rprint("[bold]Writing[/bold] IS outputs ...")
        write_json(unified, region="is")
        return unified

    if region == "li":
        rprint(f"[bold]Fetching[/bold] LI VAT rates (mirror CH) ...")
        li_data = fetch_li_vat_rates()
        html = li_data.get("html", "")
        rprint("[bold]Parsing[/bold] LI (from CH) to unified model ...")
        li_rates = parse_li_html(html)
        unified = {
            "countries": [{
                "iso2": li_rates["iso2"],
                "name": li_rates["country"],
                "categories": li_rates["categories"],
            }]
        }
        rprint("[bold]Writing[/bold] LI outputs ...")
        write_json(unified, region="li")
        return unified

    if region == "ca":
        rprint(f"[bold]Building[/bold] CA GST/HST by province (step 1) ...")
        data = fetch_ca_vat_rates()
        ca_rates = parse_ca(data.get('provinces', []))
        rprint("[bold]Writing[/bold] CA outputs ...")
        write_json(ca_rates, region="ca")
        return ca_rates

    rprint(f"[yellow]Unknown region '{region}'. Skipping.[/yellow]")
    return None


