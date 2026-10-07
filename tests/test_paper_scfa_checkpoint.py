"""Keep the manuscript's measured verdict and development scope explicit."""
import importlib.util
from pathlib import Path


def test_scfa_paper_preserves_threshold_and_scope():
    spec = importlib.util.spec_from_file_location('checkpoint', Path('paper/paper_scfa_checkpoint.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    class Collector:
        def __init__(self):
            self.text = []
            self.tables = []
        def h(self, text): self.text.append(text)
        def p(self, text): self.text.append(text)
        def table(self, headers, rows, caption): self.tables.append((headers, rows, caption))

    paper = Collector()
    module.add(paper)
    text = ' '.join(paper.text)
    for phrase in ['useful_win=False', '9.43 percent', '84 subjects',
                   'not an untouched holdout', 'ten small fits',
                   'Hexanoic acid', 'metadata-only']:
        assert phrase in text
    assert len(paper.tables) == 1
    assert len(paper.tables[0][1]) == 4
