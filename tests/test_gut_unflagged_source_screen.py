import json
from scripts.gut_unflagged_source_screen import run,IDS

def test_live_screen_is_source_description_only():
    x=json.load(open('results/gut_unflagged_source_screen.json'))
    assert x['n_rows']==8 and {r['accession'] for r in x['rows']}==set(IDS)
    assert all(r['http_status']==200 and len(r['response_sha256'])==64 for r in x['rows'] if r['http_status']==200)
    assert all(r['assay_status'] in {'study_description_only_not_run_verified','unknown','unverifiable_network_error'} for r in x['rows'])
    assert all('study-abstract' not in r for r in x['rows'])

def test_accession_mismatch_fails_closed():
    class R:
        status_code=200
        content=b'{}'
        def json(self):return {'data':{'attributes':{'accession':'wrong'}}}
    try:run(fetch=lambda url,timeout:R())
    except ValueError as e:assert 'accession mismatch' in str(e)
    else:raise AssertionError('mismatch passed')
