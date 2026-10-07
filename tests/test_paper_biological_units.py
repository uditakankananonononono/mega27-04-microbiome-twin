"""Biological-unit prose keeps invented examples separate from results."""
import importlib.util
from pathlib import Path


def test_biological_unit_scope():
    spec = importlib.util.spec_from_file_location('units', Path('paper/paper_biological_units.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    class Collector:
        def __init__(self): self.text=[]
        def h(self, value): self.text.append(value)
        def p(self, value): self.text.append(value)
    paper=Collector()
    module.add(paper)
    text=' '.join(paper.text)
    for phrase in ['hypothetical counts, not a new empirical result',
                   'insufficient studies', 'external-win certification false',
                   'strictly earlier baseline', 'introduces no fresh fit']:
        assert phrase in text
    assert round(91/110,4) == 0.8273
    assert (0.9+0.1)/2 == 0.5
