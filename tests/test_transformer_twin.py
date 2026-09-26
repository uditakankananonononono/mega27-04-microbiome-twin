import numpy as np
import torch
from microtwin.models import TransformerTwin
from microtwin.evaluate import fit_predict


def test_transformer_mask_and_simplex():
    model = TransformerTwin(4, d=16, heads=4).eval()
    z = torch.tensor([[.5,.5,0,0], [0,.5,.5,0]], dtype=torch.float32)
    with torch.no_grad(): p = model(z).numpy()
    assert np.allclose(p.sum(1), 1)
    assert (p[z.numpy()==0] == 0).all()


def test_model_family_can_fit_tiny_task(monkeypatch):
    import microtwin.evaluate as evaluate
    monkeypatch.setitem(evaluate.EPOCHS, 'transformer', 3)
    z = np.array([[.5,.5,0],[0,.5,.5],[.5,0,.5],[1/3,1/3,1/3]],float)
    p = np.array([[.4,.6,0],[0,.6,.4],[.7,0,.3],[.2,.5,.3]],float)
    out = fit_predict('transformer', z[:3], p[:3], z[3:], seed=0)
    assert out.shape == (1,3) and np.isfinite(out).all() and np.isclose(out.sum(),1)
