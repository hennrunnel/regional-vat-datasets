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
    ]
    lines.extend(header)
    
    # Build final region set: always include EU and UK if data files exist
    regions_to_render = set([r.lower() for r in selected_regions])
    for fixed in ['eu', 'uk']:
        regions_to_render.add(fixed)

    # EU section - always try to load from file
    if 'eu' in regions_to_render:
        lines.extend([
            '## EU (European Union)',
            '- Sources:',
            '  - TEDB (EC UI): https://ec.europa.eu/taxation_customs/tedb/#/home',
            '  - TEDB VAT SOAP WSDL: https://ec.europa.eu/taxation_customs/tedb/ws/VatRetrievalService.wsdl',
            '- Schema:',
            '  - country_fields: iso2, name',
            '  - category_fields: label, rate_percent, category_id, rate_type',
            '',
        ])
        
        # Load EU data from file
        eu_data_path = Path('data/eu/parsed/latest.json')
        if eu_data_path.exists():
            try:
                eu_data = json.loads(eu_data_path.read_text())
                eu_countries = eu_data.get('countries', [])
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
            except Exception as e:
                lines.extend(['', f'_EU data available but parsing failed: {e}_'])
        else:
            lines.extend(['', '_EU data not yet fetched._'])
    
    # UK section - always try to load from file
    if 'uk' in regions_to_render:
        lines.extend([
            '',
            '## UK (United Kingdom)',
            '- Sources:',
            '  - GOV.UK VAT rates: https://www.gov.uk/guidance/rates-of-vat-on-different-goods-and-services',
            '- Schema:',
            '  - country_fields: iso2, name',
            '  - category_fields: label_short (preferred), label, rate_percent, rate_type, group, reference',
            '',
        ])
        
        # Load UK data from file
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
                            label = str(cat.get('label_short') or cat.get('label') or '')
                            rate = cat.get('rate_percent')
                            rate_s = str(rate) if rate is not None else 'N/A'
                            lines.append(f"| {iso2} | {country} | {label} | {rate_s} |")
            except Exception as e:
                lines.extend(['', f'_UK data available but parsing failed: {e}_'])
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
    
    # Other regions
    region_names = {
        'ch': 'Switzerland',
        'no': 'Norway',
        'is': 'Iceland',
        'ca': 'Canada',
    }
    for r in sorted(regions_to_render):
        if r.lower() not in ['eu', 'uk']:
            pretty = region_names.get(r.lower(), r.upper())
            lines.extend(['', f"## {pretty}", '- Sources:'])
            if r.lower() == 'ch':
                lines.append('  - Swiss FTA VAT rates: https://www.estv.admin.ch/estv/en/home/mehrwertsteuer/mwst-steuersaetze.html')
            if r.lower() == 'no':
                lines.append('  - Skatteetaten VAT rates: https://www.skatteetaten.no/en/business-and-organisation/vat/rates-and-registration/vat-rates/')
            if r.lower() == 'is':
                lines.append('  - RSK VAT rates: https://www.rsk.is/english/companies/value-added-tax/vat-rates/')
            if r.lower() == 'li':
                lines.append('  - Mirrors Switzerland VAT rates (CH)')
            if r.lower() == 'ca':
                lines.append('  - CRA GST/HST rates: https://www.canada.ca/en/revenue-agency/services/tax/businesses/topics/gst-hst/charge-collect-which-rate.html')
            lines.extend(['- Schema:', '  - country_fields: iso2, name', '  - category_fields: label, rate_percent', ''])
            data_path = Path(f'data/{r.lower()}/parsed/latest.json')
            if data_path.exists():
                try:
                    data = json.loads(data_path.read_text())
                    countries = data.get('countries', [])
                    if countries:
                        lines.extend(['### ' + pretty + ' Dataset (full)', '', '| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(['---'] * len(headers)) + ' |'])
                        for c in countries:
                            iso2 = c.get('iso2', '')
                            country = c.get('name', '')
                            for cat in c.get('categories', []):
                                label = str(cat.get('label', ''))
                                rate = cat.get('rate_percent')
                                rate_s = str(rate)
                                lines.append(f"| {iso2} | {country} | {label} | {rate_s} |")
                        # Region-specific citations
                        if r.lower() == 'ch':
                            lines.extend([
                                '',
                                'References (CH):',
                                '- FTA VAT rates: https://www.estv.admin.ch/estv/en/home/mehrwertsteuer/mwst-steuersaetze.html',
                            ])
                        if r.lower() == 'ca':
                            lines.extend([
                                '',
                                'References (CA federal zero-rated):',
                                '- Basic groceries: https://www.canada.ca/en/revenue-agency/services/forms-publications/publications/gi-001/basic-groceries.html',
                                '- Prescription drugs: https://www.canada.ca/en/revenue-agency/services/forms-publications/publications/gi-063/prescription-drugs.html',
                                '- Medical devices: https://www.canada.ca/en/revenue-agency/services/forms-publications/publications/gi-067/medical-devices.html',
                                '- Books: https://www.canada.ca/en/revenue-agency/services/forms-publications/publications/gi-065/books.html',
                            ])
                except Exception:
                    lines.extend(['', f'_{pretty} data available but parsing failed._'])
            else:
                lines.extend(['', f'_{pretty} data not yet fetched._'])
    
    # Notes
    lines.extend([
        '',
        '### Notes',
        '',
        '- TEDB is the authoritative EC source for EU VAT rates.',
        '- GOV.UK is the authoritative source for UK VAT rates.',
        '- Latest per category is selected by situationOn (EU) or current rates (UK).',
        '- UK categories are mapped to EU equivalents where possible for consistency.',
    ])
    
    out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return out


