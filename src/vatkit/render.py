import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def write_json(unified: Dict[str, Any], region: str = 'eu') -> Path:
    out = Path(f'data/{region}/parsed/latest.json')
    ensure_dir(out.parent)
    out.write_text(json.dumps(unified, indent=2, ensure_ascii=False) + "\n", encoding='utf-8')
    return out


def write_markdown(unified: Dict[str, Any], selected_regions: List[str]) -> Path:
    out = Path('README.md')
    # Build table header
    headers = ['iso2', 'country', 'category_label', 'rate_percent']
    lines = []
    
    # Always use today's UTC date
    today_utc = datetime.utcnow().date().isoformat()
    
    # Plain text header (no YAML frontmatter)
    header = [
        '# Regional VAT Datasets',
        '',
        f'- Retrieved at: {today_utc} (UTC)',
        "- Context: Public datasets that feed Voog's upcoming multi‑VAT support. Each region keeps its own sources and category semantics.",
        '',
        '## EU (European Union)',
        '- Sources:',
        '  - TEDB (EC UI): https://ec.europa.eu/taxation_customs/tedb/#/home',
        '  - TEDB VAT SOAP WSDL: https://ec.europa.eu/taxation_customs/tedb/ws/VatRetrievalService.wsdl',
        '- Schema:',
        '  - country_fields: iso2, name',
        '  - category_fields: label, rate_percent, category_id, rate_type',
        '',
    ]
    lines.extend(header)
    
    # EU dataset
    eu_countries = unified.get('countries', []) if 'eu' in selected_regions else []
    if eu_countries:
        lines.extend([
            f'- Coverage: EU members = {len(eu_countries)}',
            '',
            '### EU Dataset (full)',
            '',
            '| ' + ' | '.join(headers) + ' |',
            '| ' + ' | '.join(['---'] * len(headers)) + ' |',
        ])
        for c in eu_countries:
            iso2 = c.get('iso2', '')
            country = c.get('name', '')
            for cat in c.get('categories', []):
                label = str(cat.get('label', ''))
                rate = cat.get('rate_percent')
                rate_s = str(rate)
                lines.append(f"| {iso2} | {country} | {label} | {rate_s} |")
    
    # UK section
    if 'uk' in selected_regions:
        lines.extend([
            '',
            '## UK (United Kingdom)',
            '- Sources:',
            '  - GOV.UK VAT rates: https://www.gov.uk/guidance/rates-of-vat-on-different-goods-and-services',
            '- Schema:',
            '  - country_fields: iso2, name',
            '  - category_fields: label, rate_percent, description',
            '',
        ])
        
        # Try to load UK data if available
        uk_data_path = Path('data/uk/parsed/latest.json')
        if uk_data_path.exists():
            try:
                uk_data = json.loads(uk_data_path.read_text())
                uk_countries = uk_data.get('countries', [])
                if uk_countries:
                    lines.extend([
                        f'- Coverage: UK regions = {len(uk_countries)}',
                        '',
                        '### UK Dataset (full)',
                        '',
                        '| ' + ' | '.join(headers) + ' |',
                        '| ' + ' | '.join(['---'] * len(headers)) + ' |',
                    ])
                    for c in uk_countries:
                        iso2 = c.get('iso2', '')
                        country = c.get('name', '')
                        for cat in c.get('categories', []):
                            label = str(cat.get('label', ''))
                            rate = cat.get('rate_percent')
                            rate_s = str(rate) if rate is not None else 'N/A'
                            lines.append(f"| {iso2} | {country} | {label} | {rate_s} |")
            except Exception:
                lines.extend(['', '_UK data available but parsing failed._'])
        else:
            lines.extend(['', '_UK data not yet fetched._'])
    
    # Intro with Voog blurb and CTA
    intro = [
        '',
        'This repository feeds Voog\'s upcoming multi-VAT support to help merchants stay compliant across multiple regions.',
        'Voog lets you build multilingual websites and online stores that scale internationally.',
        '[Start your 30‑day free trial](https://www.voog.com).',
        '',
        '### Usage',
        '',
        '```bash',
        'python3 -m venv .venv',
        'source .venv/bin/activate',
        'pip install -r requirements.txt',
        'PYTHONPATH=src python -m vatkit.cli',
        '```',
        '',
        'This will fetch from TEDB (EU), GOV.UK (UK), map categories, and update this README and region-specific JSON files.',
        '',
        'Official VAT category references:',
        '- EU: Annex III to the VAT Directive (eligible reduced-rate categories): https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=celex%3A32006L0112#d1e32-69-1',
        '- EU: TEDB documentation entry point: https://ec.europa.eu/taxation_customs/tedb/#/home',
        '- UK: GOV.UK VAT rates guidance: https://www.gov.uk/guidance/rates-of-vat-on-different-goods-and-services',
        '',
    ]
    lines.extend(intro)
    
    # Other regions placeholder
    region_names = {
        'ch': 'Switzerland',
        'no': 'Norway',
        'is': 'Iceland',
        'ca': 'Canada',
    }
    for r in selected_regions:
        if r.lower() not in ['eu', 'uk']:
            lines.extend(['', f"## {region_names.get(r.lower(), r.upper())}", '', '_Coming soon (adapter stubbed)._'])
    
    # Notes
    lines.extend([
        '',
        '### Notes',
        '',
        '- TEDB is the authoritative EC source for EU VAT rates.',
        '- GOV.UK is the authoritative source for UK VAT rates.',
        '- Latest per category is selected by situationOn (EU) or current rates (UK).',
    ])
    
    out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return out


