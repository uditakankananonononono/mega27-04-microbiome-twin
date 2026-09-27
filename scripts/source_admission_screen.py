"""Screen the eight viewed MGnify metadata records through the local gate."""
import json
from pathlib import Path
from microtwin.source_admission import assess_many
ROOT=Path(__file__).resolve().parents[1]
def run():
    d=json.loads((ROOT/'results/metadata_integrity_matrix.json').read_text())
    if d['n_studies']!=len(d['rows']):raise ValueError('matrix row count')
    return assess_many(d['rows'])
if __name__=='__main__':
    x=run();(ROOT/'results/source_admission_screen.json').write_text(json.dumps(x,indent=2)+'\n')
    print('blocked',x['blocked'],'metadata-ready',x['metadata_ready_for_manual_review'])
