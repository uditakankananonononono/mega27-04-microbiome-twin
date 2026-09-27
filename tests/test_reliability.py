import pytest
from microtwin.reliability import reliability_report, COMPONENTS


def test_no_composite_even_with_all_evidence_until_calibrated():
    r = reliability_report({k:{"value": .5,"source":"held-out-study"} for k in COMPONENTS},
                           calibration_registry={"weights":[.2]*5}, domain="oral")
    assert r["all_components_present"]
    assert r["twin_reliability_index"] is None
    assert r["index_status"] == "unavailable_no_independently_validated_calibrator"


def test_missing_component_and_empty_provenance_exposed():
    assert reliability_report({})["components"]["transferability"]["status"] == "missing"
    with pytest.raises(ValueError,match="source"):
        reliability_report({"prediction_accuracy":{"value":.3,"source":""}})


@pytest.mark.parametrize('value',[True,False,float('nan'),float('inf')])
def test_component_rejects_boolean_and_nonfinite(value):
    with pytest.raises(ValueError,match='finite'):
        reliability_report({'prediction_accuracy':{'value':value,'source':'test'}})


@pytest.mark.parametrize('source',[None,{},[],42,'  '])
def test_component_source_must_be_nonblank_string(source):
    with pytest.raises(ValueError,match='source'):
        reliability_report({'prediction_accuracy':{'value':.5,'source':source}})


def test_domain_must_be_meaningful_if_supplied():
    for domain in (True,[],{},'  '):
        with pytest.raises(ValueError,match='domain'):
            reliability_report({},domain=domain)
    assert reliability_report({},domain='oral')['domain']=='oral'
