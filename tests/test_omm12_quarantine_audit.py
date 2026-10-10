import pytest
from scripts.omm12_quarantine_audit import classification,require_allowed,LABEL

@pytest.mark.parametrize('kind,literal,formula,status',[
 ('n','3.4',False,'NUMERIC_REPRESENTATION_VALID'),
 ('n','0',False,'AMBIGUOUS_ZERO'),
 ('n',None,False,'AMBIGUOUS_MISSING'),
 ('e','#N/A',False,'LITERAL_ERROR'),
 ('s','N/A',False,'LITERAL_FLAG'),
 ('n','-2',False,'REJECT_NONFINITE_OR_NEGATIVE'),
 ('n','nan',False,'REJECT_NONFINITE_OR_NEGATIVE'),
 ('n','1',True,'REJECT_FORMULA'),
 ('b','1',False,'REJECT_TYPE'),
 ('s','other',False,'REJECT_UNEXPECTED_TEXT')])
def test_raw_representation(kind,literal,formula,status):
    assert classification(kind,literal,formula)==status

def test_manifest_guard():
    require_allowed('B2',{'B2'})
    with pytest.raises(ValueError,match='OFF_MANIFEST'):require_allowed('N2',{'B2'})

def test_no_newbatch_or_other_medium_selection():
    assert LABEL.fullmatch('OMM12_E1_AF_W1')
    assert not LABEL.fullmatch('OMM12_S1new_APF_W1')
    assert not LABEL.fullmatch('OMM12_E1_GAM_W1')

def test_published_status_cannot_admit_quantitative_outcomes():
    import json
    from scripts.omm12_quarantine_audit import ROOT
    d=json.loads((ROOT/'results/omm12_quarantine_certificate_20261010.json').read_text())
    assert d['structural_C1']=='ADMITTED_DOCUMENTARY_REPRESENTATION_COUNTS_ONLY'
    assert d['quantitative_C1']=='NOT_ADMITTED_LOCKED'
    assert d['zero_semantics']=='UNRESOLVED'
    assert d['quantitative_admission']=='NOT_ADMITTED'
    assert d['C2']=='BLOCKED' and d['C3']=='NOT_PROPOSED'
    assert d['useful_win']=='NOT_TESTED'
