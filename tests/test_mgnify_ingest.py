import pytest
from microtwin.mgnify_ingest import select_run_columns


def _analysis(sample, run=None, assembly=None):
    return {"relationships": {"sample": {"data": {"id": sample}},
            "run": {"data": {"id": run}} if run else {"data": None},
            "assembly": {"data": {"id": assembly}} if assembly else {"data": None}}}


def test_run_only_when_assembly_duplicates_sample():
    result = select_run_columns(["ERR1", "ERR2", "ERZ1"],
                                [_analysis("S1", run="ERR1"), _analysis("S1", assembly="ERZ1"),
                                 _analysis("S2", run="ERR2")])
    assert result["sample_count"] == 2
    assert result["selected_run_columns"] == ["ERR1", "ERR2"]
    assert result["excluded_assembly_columns"] == ["ERZ1"]


def test_ambiguous_run_mapping_rejected():
    with pytest.raises(ValueError, match="ambiguous"):
        select_run_columns(["ERR1", "ERR2"], [_analysis("S1", run="ERR1"), _analysis("S1", run="ERR2")])


def test_unexplained_column_rejected():
    with pytest.raises(ValueError, match="unexplained"):
        select_run_columns(["ERR1", "OTHER"], [_analysis("S1", run="ERR1")])
