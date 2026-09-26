"""Composition predictors phi: assemblage z -> composition p on the simplex.

All models respect the two structural constraints of the problem:
  (i)  absent taxa get exactly zero abundance (masking),
  (ii) predictions lie on the probability simplex.

Models
------
PresenceMean   : p_i ∝ z_i * mean_train(p_i)            (null baseline)
CNODE          : dx/dt = x ⊙ (Wz - 1 xᵀWz), x(0)=z, p = x(1)
                 (re-implementation of Michel-Mata et al. 2022)
GLVSteady      : replicator with pairwise interactions A: dx/dt = x⊙(r + A x - φ)
                 integrated to t=T (a generalized Lotka-Volterra style baseline)
GraphTwin      : ours - a message-passing graph network on the complete graph of
                 *present* taxa. Node i carries a learned embedding e_i; each
                 layer computes attention-weighted messages
                     m_i = Σ_{j∈S, j≠i} α_ij V h_j ,  α_ij = softmax_j(q_iᵀk_j/√d)
                 and a learned edge gate g_ij = σ(e_iᵀ U e_j) modulating α,
                 then h_i ← LayerNorm(h_i + MLP([h_i, m_i])). Output logits are
                 added to a log-prior (log mean abundance) and passed through a
                 masked softmax over S.
"""
from __future__ import annotations

import math

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


def bc_loss(p: torch.Tensor, q: torch.Tensor) -> torch.Tensor:
    return ((p - q).abs().sum(1) / (p + q).sum(1).clamp(min=1e-12)).mean()


def masked_softmax(logits: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
    logits = logits.masked_fill(mask <= 0, -1e9)
    return torch.softmax(logits, dim=-1) * (mask > 0)


class PresenceMean:
    name = "presence_mean"

    def fit(self, Z, P):
        self.mu = P.mean(0) + 1e-9
        return self

    def predict(self, Z):
        q = (Z > 0) * self.mu
        return q / q.sum(1, keepdims=True)


class CNODE(nn.Module):
    name = "cnode"

    def __init__(self, n: int, steps: int = 20):
        super().__init__()
        self.W = nn.Parameter(torch.zeros(n, n))  # zero init: identity map at start
        self.steps = steps

    def forward(self, z):
        x = z
        h = 1.0 / self.steps
        f = z @ self.W.T  # fitness depends on assemblage only (cNODE1)

        def rhs(x):
            return x * (f - (x * f).sum(1, keepdim=True))
        for _ in range(self.steps):  # RK4
            k1 = rhs(x); k2 = rhs(x + h / 2 * k1); k3 = rhs(x + h / 2 * k2); k4 = rhs(x + h * k3)
            x = x + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        x = x.clamp(min=0) * (z > 0)
        return x / x.sum(1, keepdim=True).clamp(min=1e-12)


class GLVSteady(nn.Module):
    name = "glv"

    def __init__(self, n: int, steps: int = 30, T: float = 3.0):
        super().__init__()
        self.r = nn.Parameter(torch.zeros(n))
        self.A = nn.Parameter(torch.zeros(n, n))
        self.steps, self.T = steps, T

    def forward(self, z):
        x = z; h = self.T / self.steps
        for _ in range(self.steps):
            fit = self.r + x @ self.A.T
            x = x + h * x * (fit - (x * fit).sum(1, keepdim=True))
            x = x.clamp(min=0) * (z > 0)
            x = x / x.sum(1, keepdim=True).clamp(min=1e-12)
        return x


class GraphTwin(nn.Module):
    name = "graphtwin"

    def __init__(self, n: int, d: int = 32, layers: int = 2, prior: np.ndarray | None = None,
                 dropout: float = 0.1):
        super().__init__()
        self.emb = nn.Parameter(torch.randn(n, d) * 0.1)
        self.q = nn.ModuleList(nn.Linear(d, d, bias=False) for _ in range(layers))
        self.k = nn.ModuleList(nn.Linear(d, d, bias=False) for _ in range(layers))
        self.v = nn.ModuleList(nn.Linear(d, d, bias=False) for _ in range(layers))
        self.U = nn.Parameter(torch.zeros(d, d))
        self.mlp = nn.ModuleList(nn.Sequential(nn.Linear(2 * d, d), nn.GELU(), nn.Linear(d, d))
                                 for _ in range(layers))
        self.norm = nn.ModuleList(nn.LayerNorm(d) for _ in range(layers))
        self.out = nn.Linear(d, 1)
        nn.init.zeros_(self.out.weight); nn.init.zeros_(self.out.bias)
        lp = np.log(prior + 1e-6) if prior is not None else np.zeros(n)
        self.register_buffer("logprior", torch.tensor(lp, dtype=torch.float32))
        self.drop = nn.Dropout(dropout); self.d = d

    def forward(self, z):
        mask = (z > 0).float()                      # B x n
        B, n = mask.shape
        h = self.emb.unsqueeze(0).expand(B, n, self.d)
        gate = torch.sigmoid(self.emb @ self.U @ self.emb.T)  # n x n learned edge gate
        pair = mask.unsqueeze(1) * mask.unsqueeze(2)          # B x n x n present-present
        eye = torch.eye(n, device=z.device).unsqueeze(0)
        pair = pair * (1 - eye)
        for q, k, v, mlp, norm in zip(self.q, self.k, self.v, self.mlp, self.norm):
            att = (q(h) @ k(h).transpose(1, 2)) / math.sqrt(self.d)
            att = att.masked_fill(pair <= 0, -1e9)
            a = torch.softmax(att, -1) * pair * gate
            m = a @ v(h)
            h = norm(h + self.drop(mlp(torch.cat([h, m], -1))))
        logits = self.out(h).squeeze(-1) + self.logprior
        return masked_softmax(logits, mask)


def train_torch(model: nn.Module, Z: np.ndarray, P: np.ndarray, epochs: int = 300,
                lr: float = 0.01, wd: float = 1e-4, batch: int = 32, seed: int = 0) -> nn.Module:
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    Zt = torch.tensor(Z, dtype=torch.float32); Pt = torch.tensor(P, dtype=torch.float32)
    opt = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=wd)
    n = len(Z)
    for _ in range(epochs):
        model.train()
        idx = rng.permutation(n)
        for b in range(0, n, batch):
            ib = torch.tensor(idx[b:b + batch])
            opt.zero_grad(); bc_loss(model(Zt[ib]), Pt[ib]).backward(); opt.step()
    model.eval()
    return model


def predict_torch(model: nn.Module, Z: np.ndarray) -> np.ndarray:
    with torch.no_grad():
        return model(torch.tensor(Z, dtype=torch.float32)).numpy()


class TwinStack(nn.Module):
    """Assemblage-conditioned convex stacking of base predictors (GraphTwin v2).

    p(x) = sum_m w_m(z) * p_m(x), w(z) = softmax(MLP(phi(z))).
    phi(z) = [richness, richness/n, presence-weighted prior entropy, mean taxon embedding].
    The gate sees only assemblage summaries; base predictions come from frozen,
    already-fitted base models (stacking protocol in evaluate.fit_predict).
    """
    name = "graphtwin2"
    BASES = ("presence_mean", "cnode", "glv", "graphtwin")

    def __init__(self, n: int, prior: np.ndarray, d_emb: int = 16, hidden: int = 16):
        super().__init__()
        self.emb = nn.Parameter(torch.randn(n, d_emb) * 0.1)
        self.mlp = nn.Sequential(nn.Linear(3 + d_emb, hidden), nn.GELU(), nn.Linear(hidden, len(self.BASES)))
        nn.init.zeros_(self.mlp[-1].weight); nn.init.zeros_(self.mlp[-1].bias)  # start uniform
        lp = np.log(prior + 1e-6)
        self.register_buffer("logprior", torch.tensor(lp, dtype=torch.float32))

    def phi(self, z: torch.Tensor) -> torch.Tensor:
        mask = (z > 0).float()
        rich = mask.sum(1, keepdim=True)
        ent = -(mask * self.logprior).sum(1, keepdim=True) / rich.clamp(min=1.0)
        mean_emb = (mask.unsqueeze(-1) * self.emb.unsqueeze(0)).sum(1) / rich.clamp(min=1.0)
        n = torch.tensor(float(z.shape[1]), device=z.device)
        return torch.cat([rich, rich / n, ent, mean_emb], dim=1)

    def weights(self, z: torch.Tensor) -> torch.Tensor:
        return torch.softmax(self.mlp(self.phi(z)), dim=-1)

    def combine(self, z: torch.Tensor, base_preds: torch.Tensor) -> torch.Tensor:
        """base_preds: B x M x n (each on the simplex, absence-masked)."""
        w = self.weights(z).unsqueeze(-1)                    # B x M x 1
        p = (w * base_preds).sum(1)                          # B x n
        return p / p.sum(1, keepdim=True).clamp(min=1e-12)


class ConstStack(nn.Module):
    """graphtwin2b: constant per-dataset simplex weights over a base subset."""
    name = "graphtwin2b"

    def __init__(self, n_bases: int):
        super().__init__()
        self.logits = nn.Parameter(torch.zeros(n_bases))

    def combine(self, base_preds: torch.Tensor) -> torch.Tensor:
        w = torch.softmax(self.logits, 0).unsqueeze(0).unsqueeze(-1)  # 1 x M x 1
        p = (w * base_preds).sum(1)
        return p / p.sum(1, keepdim=True).clamp(min=1e-12)


class CNODE2(nn.Module):
    """Two stacked cNODE1 layers trained end-to-end (Michel-Mata 2022's cNODE2)."""
    name = "cnode2"

    def __init__(self, n: int, steps: int = 20):
        super().__init__()
        self.l1 = CNODE(n, steps=steps)
        self.l2 = CNODE(n, steps=steps)

    def forward(self, z):
        return self.l2(self.l1(z))

class TransformerTwin(nn.Module):
    """Small taxon-token self-attention baseline for assemblage-to-composition.

    This is an experimental model family, not a microbiome foundation model.
    No pretrained weights or cross-study claims are implied.
    """
    name = "transformer"

    def __init__(self, n: int, d: int = 32, heads: int = 4, layers: int = 2,
                 prior: np.ndarray | None = None):
        super().__init__()
        if d % heads:
            raise ValueError("embedding dimension must be divisible by attention heads")
        self.embedding = nn.Embedding(n, d)
        self.blocks = nn.ModuleList([
            nn.TransformerEncoderLayer(d_model=d, nhead=heads, dim_feedforward=2*d,
                                       dropout=0.0, batch_first=True, norm_first=True)
            for _ in range(layers)])
        self.readout = nn.Linear(d, 1)
        nn.init.zeros_(self.readout.weight)
        nn.init.zeros_(self.readout.bias)
        p = np.asarray(prior if prior is not None else np.ones(n)/n, dtype=float)
        if p.shape != (n,) or (p < 0).any() or not np.isfinite(p).all() or p.sum() <= 0:
            raise ValueError("prior must be a finite nonnegative vector")
        self.register_buffer("logprior", torch.tensor(np.log(p + 1e-6), dtype=torch.float32))

    def forward(self, z):
        present = z > 0
        # An all-absent input is undefined; callers validate sample mass.
        if (~present.any(1)).any():
            raise ValueError("all-absent sample")
        B, n = z.shape
        tokens = self.embedding(torch.arange(n, device=z.device))[None].expand(B, n, -1)
        for block in self.blocks:
            tokens = block(tokens, src_key_padding_mask=~present)
        logits = self.readout(tokens).squeeze(-1) + self.logprior
        return masked_softmax(logits, present.float())
