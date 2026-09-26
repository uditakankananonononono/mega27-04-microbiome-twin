import pandas as pd
import pytest
from microtwin.genus_harmonize import terminal_genus


def test_excludes_hierarchy_and_species_children():
    t = pd.DataFrame({"S1": [10, 5, 2, 1]}, index=["p__Firmicutes", "p__Firmicutes;g__Bacillus",
                                                        "p__Firmicutes;g__Bacillus;s__B_cereus", "g__Lactobacillus"])
    g, report = terminal_genus(t)
    assert g.index.tolist() == ["Bacillus", "Lactobacillus"]
    assert g.S1.tolist() == [5, 1] and report["excluded_non_genus_or_unnamed_rows"] == 2


def test_genus_collision_fails_closed():
    t = pd.DataFrame({"S1": [1, 2]}, index=["p__A;g__Shared", "p__B;g__Shared"])
    with pytest.raises(ValueError, match="collision"):
        terminal_genus(t)
