"""Preserve the manuscript's operational interpretation boundaries."""
import importlib.util
from pathlib import Path


def test_operational_scope_text():
    spec = importlib.util.spec_from_file_location('operational', Path('paper/paper_operational_contract.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    class Collector:
        def __init__(self): self.text = []
        def h(self, value): self.text.append(value)
        def p(self, value): self.text.append(value)
    paper = Collector()
    module.add(paper)
    text = ' '.join(paper.text)
    for phrase in ['not a hosted patient service', 'cross-source prediction abstains',
                   'query-subject separation unverified', 'composite index unavailable',
                   'Replacing both an artifact and its receipt', 'adds no benchmark outcome']:
        assert phrase in text
