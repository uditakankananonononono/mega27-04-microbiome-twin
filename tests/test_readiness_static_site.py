import hashlib,json
from pathlib import Path
from microtwin.source_readiness import packet
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'docs/readiness'

def test_site_allowlist_hash_and_exact_copies():
    m=json.loads((SITE/'asset-manifest.json').read_text())
    actual={str(p.relative_to(SITE)) for p in SITE.rglob('*') if p.is_file() and p.name!='asset-manifest.json'}
    assert actual==set(m['files'])
    assert m['total_bytes']<30_000_000
    for name,r in m['files'].items():
        p=SITE/name;b=p.read_bytes()
        assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256']
        if r['origin'].startswith(('src/','results/','web/')):assert b==(ROOT/r['origin']).read_bytes()
        assert not name.endswith(('.xlsx','.csv','.tsv'))
        assert 'quarantine/tab1' not in name and 'source-data' not in name

def test_hosted_python_parity_and_scientific_boundaries():
    assert packet(SITE/'assets')==packet(ROOT/'results')
    r=packet(SITE/'synthetic');assert r['status']=='DECLARATIONS_READY_FOR_MANUAL_REVIEW'
    assert r['quantitative_C1']=='NOT_ADMITTED_LOCKED' and not r['auto_admission']

def test_no_remote_scripts_telemetry_or_upload():
    js=(SITE/'app.js').read_text();html=(SITE/'index.html').read_text()
    assert 'https://' not in js
    assert 'localStorage' not in js and 'POST' not in js and 'XMLHttpRequest' not in js
    assert 'type="file"' not in html and '<form' not in html
    assert 'No outcomes. No uploads. No clinical advice.' in html
    assert 'wasm-unsafe-eval' in html
