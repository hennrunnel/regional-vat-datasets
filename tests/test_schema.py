import json
from pathlib import Path


def load(path):
    p = Path(path)
    assert p.exists(), f"Missing file: {path}"
    return json.loads(p.read_text())


def test_eu_schema():
    data = load('data/eu/parsed/latest.json')
    assert 'countries' in data and isinstance(data['countries'], list)
    assert len(data['countries']) >= 20


def test_uk_schema():
    data = load('data/uk/parsed/latest.json')
    assert 'countries' in data
    c = data['countries'][0]
    assert c['iso2'] == 'GB'
    labels = [cat['label'] if 'label' in cat else cat.get('label_short') for cat in c['categories']]
    assert any('Standard' in (l or '') for l in labels)


def test_ch_rates():
    data = load('data/ch/parsed/latest.json')
    cats = {c['label']: c['rate_percent'] for c in data['countries'][0]['categories']}
    assert cats.get('Standard') == 8.1
    assert cats.get('Accommodation') == 3.8


def test_no_rates():
    data = load('data/no/parsed/latest.json')
    cats = {c['label']: c['rate_percent'] for c in data['countries'][0]['categories']}
    assert cats.get('Standard') == 25.0
    assert cats.get('Foodstuffs') == 15.0


def test_is_rates():
    data = load('data/is/parsed/latest.json')
    cats = {c['label']: c['rate_percent'] for c in data['countries'][0]['categories']}
    assert cats.get('Standard') == 24.0
    assert cats.get('Accommodation') == 11.0


def test_ca_schema():
    data = load('data/ca/parsed/latest.json')
    countries = data['countries']
    assert any(c['iso2'] == 'CA-AB' for c in countries)
    assert any(c['iso2'] == 'CA-QC' for c in countries)

