from pathlib import Path


def test_manuscript_scope_updates():
    text=Path('paper/build_paper.py').read_text()
    assert '(private). Commands:' not in text
    assert 'Historical blind reproduction snapshot' in text
    assert 'not 169 independent primary biological datasets' in text
    assert 'falsified that scoring-only explanation' in text
    assert 'Those tables have not been certified as independent external biological studies' in text


def test_cover_and_extension_scope():
    text=Path('paper/build_paper.py').read_text()
    assert 'DRAFT: Interaction Models Lower Prediction Error in 121 of 160 MGnify Study Tables' in text
    assert 'literature priority is not established here' in text
    assert 'useful_win=False because the nearest-three gain misses' in text
    assert 'online September 11, 2015' in text
