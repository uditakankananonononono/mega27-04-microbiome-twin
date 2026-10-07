from pathlib import Path


def test_admission_paper_keeps_gates_and_software_scope():
    text=Path('paper/paper_resistant_starch_admission.py').read_text()
    for phrase in ['175','143','174','endpoint-selection error','admission','not eight independent','not a hosted service','No raw-read reprocessing','not an empty cohort','not a license for unrelated']:
        assert phrase in text
    assert 'r[\'outcome_numeric_parseable_counts\']' in text
    assert 'paper_resistant_starch_admission.add(P)' in Path('paper/build_paper.py').read_text()
