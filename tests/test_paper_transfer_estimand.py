"""Target restriction is not full-community validation."""
import importlib.util
from pathlib import Path
import numpy as np


def test_transfer_scope_and_example():
    spec=importlib.util.spec_from_file_location('transfer',Path('paper/paper_transfer_estimand.py'))
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    class Collector:
        def __init__(self): self.text=[]
        def h(self,value): self.text.append(value)
        def p(self,value): self.text.append(value)
    paper=Collector();module.add(paper);text=' '.join(paper.text)
    for phrase in ['analytical and hypothetical', 'changes the evaluated population',
                   'never automatic discovery certification',
                   'introduces no new cohort scoring']:
        assert phrase in text
    assert np.abs(np.array([.8,.2,0])-[.4,.1,.5]).sum()/2 == .5
