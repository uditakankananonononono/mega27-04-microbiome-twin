import pandas as pd
import pytest
from microtwin.sample_collapse import collapse_runs


def _a(sample, run=None, assembly=None):
    return {"relationships": {"sample": {"data": {"id": sample}},
            "run": {"data": {"id": run}} if run else {"data": None},
            "assembly": {"data": {"id": assembly}} if assembly else {"data": None}}}


def test_pool_runs_before_normalize_and_exclude_assembly():
    t = pd.DataFrame({"R1": [10, 0], "R2": [0, 30], "R3": [3, 2], "Z1": [100, 100]}, index=["A", "B"])
    pooled, report = collapse_runs(t, [_a("S1", "R1"), _a("S1", "R2"), _a("S2", "R3"), _a("S1", assembly="Z1")])
    assert pooled["S1"].tolist() == [10, 30]
    assert pooled["S2"].tolist() == [3, 2]
    assert report["multiple_run_samples"] == 1 and report["excluded_assembly_columns"] == 1


def test_unknown_column_or_shared_run_fails_closed():
    t = pd.DataFrame({"R1": [1], "X": [2]}, index=["A"])
    with pytest.raises(ValueError, match="unexplained"):
        collapse_runs(t, [_a("S1", "R1")])
    with pytest.raises(ValueError, match="multiple samples"):
        collapse_runs(t[["R1"]], [_a("S1", "R1"), _a("S2", "R1")])


def test_assembly_only_sample_fails_closed():
    t = pd.DataFrame({"R1": [1], "Z2": [2]}, index=["A"])
    with pytest.raises(ValueError, match="sample without a run"):
        collapse_runs(t, [_a("S1", "R1"), _a("S2", assembly="Z2")])
