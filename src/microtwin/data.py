"""Loading and preprocessing of real community-composition datasets.

Matrices are stored taxa x samples (as in the cNODE release). Following the
cNODE protocol, samples sharing the same species assemblage are de-duplicated
(one representative kept, chosen with a fixed seed), and both the assemblage
vector z and composition p are L1-normalised.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "raw" / "cnode"
DATASETS = ["Ocean", "Drosophila_Gut", "Soil_Vitro", "Soil_Vivo", "Human_Oral", "Human_Gut"]
# Median leave-one-out Bray-Curtis error reported for cNODE
# (Michel-Mata et al., iMeta 2022; PMC9221840, Results, Fig. 3A).
CNODE_PUBLISHED_MEDIAN_BC = {
    "Ocean": 0.06, "Drosophila_Gut": 0.066, "Soil_Vitro": 0.079,
    "Soil_Vivo": 0.107, "Human_Oral": 0.211, "Human_Gut": 0.242,
}


def load_raw(name: str) -> np.ndarray:
    return np.loadtxt(DATA_DIR / f"{name}.csv", delimiter=",")


def preprocess(P: np.ndarray, seed: int = 0) -> tuple[np.ndarray, np.ndarray]:
    """Return (Z, P) as samples x taxa, de-duplicated by assemblage, L1-normalised."""
    P = np.asarray(P, dtype=float).T  # samples x taxa
    keep = P.sum(1) > 0
    P = P[keep]
    Zb = (P > 0).astype(np.int8)
    rng = np.random.default_rng(seed)
    groups: dict[bytes, list[int]] = {}
    for i, z in enumerate(Zb):
        groups.setdefault(z.tobytes(), []).append(i)
    idx = sorted(int(rng.choice(g)) for g in groups.values())
    P = P[idx]; Z = Zb[idx].astype(float)
    P = P / P.sum(1, keepdims=True)
    Z = Z / Z.sum(1, keepdims=True)
    return Z, P


def load(name: str, seed: int = 0) -> tuple[np.ndarray, np.ndarray]:
    return preprocess(load_raw(name), seed=seed)


def bray_curtis(p: np.ndarray, q: np.ndarray) -> np.ndarray:
    """Row-wise Bray-Curtis dissimilarity sum|p-q| / sum(p+q)."""
    p = np.atleast_2d(p); q = np.atleast_2d(q)
    return np.abs(p - q).sum(1) / np.maximum((p + q).sum(1), 1e-12)
