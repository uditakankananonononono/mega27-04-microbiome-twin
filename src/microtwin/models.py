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
