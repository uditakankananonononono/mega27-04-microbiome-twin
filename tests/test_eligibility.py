from microtwin.eligibility import assess_records


def _row(study, accession, name="amplicon study"):
    return dict(study=study, secondary_accession=accession, biome="root:Soil",
                n_samples=25, n_genera=20, study_name=name,
                file="data/raw/mgnify/x.tsv.gz",
                source_url="https://www.ebi.ac.uk/metagenomics/api/v1/studies/x")


def test_assembly_flag_does_not_count_as_verified_cohort():
    r = assess_records([_row("A", "E1"), _row("B", "E2", "Metagenome assembly of survey")])
    assert r["manifest_rows"] == 2
    assert r["metadata_candidates"] == 1
    assert r["review_required"] == 1
    assert r["verified_independent_datasets"] == 0
    assert "possible_assembly_not_independent_biological_cohort" in r["records"][1]["reasons"]


def test_duplicate_accession_requires_review():
    r = assess_records([_row("A", "E1"), _row("B", "E1")])
    assert r["metadata_candidates"] == 0
    assert all("missing_or_duplicate_secondary_accession" in x["reasons"] for x in r["records"])
