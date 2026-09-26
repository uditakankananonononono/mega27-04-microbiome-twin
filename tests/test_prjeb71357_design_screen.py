import hashlib
import pytest
from scripts.prjeb71357_design_screen import screen

def test_header_only_run_metadata(tmp_path):
    p=tmp_path/'ena.tsv';p.write_text('run_accession\tsample_accession\tsample_title\tstudy_accession\tlibrary_strategy\n'
      'ERR1\tSAMEA1\tF1BL\tPRJEB71357\tWGA\nERR2\tSAMEA2\tF1EP\tPRJEB71357\tWGA\nERR3\tSAMEA3\tF1MP\tPRJEB71357\tWGA\nERR4\tSAMEA4\tF2BL\tPRJEB71357\tWGA\n')
    sha=hashlib.sha256(p.read_bytes()).hexdigest();x=screen(p,sha)
    assert x['subject_prefixes']==2 and x['subjects_with_all_three_phase_titles']==1
    assert 'SAMEA1' not in str(x)
    with pytest.raises(ValueError,match='checksum'):screen(p,'0'*64)
    p.write_text(p.read_text().replace('F2BL','F1BL'))
    with pytest.raises(ValueError,match='person phase'):screen(p,hashlib.sha256(p.read_bytes()).hexdigest())
