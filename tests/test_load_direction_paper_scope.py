from pathlib import Path


def test_load_direction_paper_keeps_assumption_and_gate_scope():
    text=Path('paper/paper_load_direction.py').read_text()
    for claim in ['Cartesian-box assumption','not a posterior or a confidence interval','Unknown total-load ratio','rejects zero fractions','useful_win=False','no sampling, optimization','a hosted platform endpoint','gLV witness','established rather than a new biological discovery']:
        assert claim in text
    assert 'paper_load_direction.add(P)' in Path('paper/build_paper.py').read_text()
