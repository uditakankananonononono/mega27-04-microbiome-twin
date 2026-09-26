import hashlib

import scripts.recovery_nuh_screen as mod


def test_design_screen_ignores_abundance_values(tmp_path,monkeypatch):
    source=tmp_path/'nuh.txt'
    source.write_text('LibraryID\tPatientID\tType\tDays\tGroup\tTimePoint\tk__Bacteria|p__A\n'
                      's1\tp1\tStool\t0\tCase\tPRE\tSECRET_A\n'
                      's2\tp1\tStool\t2\tCase\tDURING\tSECRET_B\n'
                      's3\tp1\tStool\t30\tCase\tPOST\tSECRET_C\n')
    monkeypatch.setattr(mod,'SRC',source)
    monkeypatch.setattr(mod,'EXPECTED',hashlib.sha256(source.read_bytes()).hexdigest())
    result=mod.screen()
    assert result['patient_labels_with_all_three_phases']==1
    assert result['taxonomic_hierarchy_columns']==1
    assert 'SECRET_A' not in str(result)
