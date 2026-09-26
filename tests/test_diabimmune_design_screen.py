import hashlib

import openpyxl

import scripts.diabimmune_design_screen as mod


def test_metadata_screen_does_not_read_abundance_rows(tmp_path,monkeypatch):
    table=tmp_path/'t.txt';table.write_text('sample\tP1_1.0\tP1_3.0\tP2_2.0\nSECRET\talpha\tbeta\tgamma\n')
    book=tmp_path/'m.xlsx'
    w=openpyxl.Workbook();g=w.active;g.title='General';g.append(['subject']);g.append(['P1']);g.append(['P2'])
    a=w.create_sheet('Antibiotics');a.append(['Subject','Age (months)']);a.append(['P1',2]);w.save(book)
    monkeypatch.setattr(mod,'MATRIX',table);monkeypatch.setattr(mod,'SUPPLEMENT',book)
    monkeypatch.setattr(mod,'EXPECTED_MATRIX',hashlib.sha256(table.read_bytes()).hexdigest())
    monkeypatch.setattr(mod,'EXPECTED_XLSX',hashlib.sha256(book.read_bytes()).hexdigest())
    result=mod.screen()
    assert result['subjects_with_any_prepost_event']==1
    assert result['matrix_subject_prefixes']==2
    assert 'SECRET' not in str(result) and 'alpha' not in str(result)
