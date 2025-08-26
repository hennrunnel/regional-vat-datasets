# Regional VAT Datasets

- Retrieved at: 2025-08-26 (UTC)
- Context: Public datasets that feed Voog's upcoming multi‑VAT support. Each region keeps its own sources and category semantics.


This repository feeds Voog's upcoming multi-VAT support to help merchants stay compliant across multiple regions.
Voog lets you build multilingual websites and online stores that scale internationally.
[Start your 30‑day free trial](https://www.voog.com).

### Usage

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src python -m vatkit.cli
```

This will fetch from TEDB (EU), GOV.UK (UK), map categories, and update this README and region-specific JSON files.

Official VAT category references:
- EU: Annex III to the VAT Directive (eligible reduced-rate categories): https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=celex%3A32006L0112#d1e32-69-1
- EU: TEDB documentation entry point: https://ec.europa.eu/taxation_customs/tedb/#/home
- UK: GOV.UK VAT rates guidance: https://www.gov.uk/guidance/rates-of-vat-on-different-goods-and-services


## Switzerland
- Sources:
  - Swiss FTA VAT rates: https://www.estv.admin.ch/estv/en/home/value-added-tax/vat-rates.html
- Schema:
  - country_fields: iso2, name
  - category_fields: label, rate_percent

### Switzerland Dataset (full)

| iso2 | country | category_label | rate_percent |
| --- | --- | --- | --- |
| CH | Switzerland | Standard | 8.1 |
| CH | Switzerland | Reduced | 2.6 |
| CH | Switzerland | Special (Accommodation) | 3.8 |

### Notes

- TEDB is the authoritative EC source for EU VAT rates.
- GOV.UK is the authoritative source for UK VAT rates.
- Latest per category is selected by situationOn (EU) or current rates (UK).
- UK categories are mapped to EU equivalents where possible for consistency.
