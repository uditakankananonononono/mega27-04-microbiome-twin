from pathlib import Path


def test_manuscript_scope_updates():
    text=Path('paper/build_paper.py').read_text()
    assert '(private). Commands:' not in text
    assert 'Historical blind reproduction snapshot' in text
    assert 'not 169 independent primary biological datasets' in text
    assert 'falsified that scoring-only explanation' in text
    assert 'Those tables have not been certified as independent external biological studies' in text
