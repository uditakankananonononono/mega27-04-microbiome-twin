"""Dynamic microbiome twin on the MDSINE2 healthy-mouse cohort (Gibson et al.,
gerberlab/MDSINE2_Paper): absolute abundances from 16S counts x qPCR totals,
generalized Lotka-Volterra with perturbation terms,

    d log x_i / dt = r_i + sum_j A_ij x_j + sum_p g_ip u_p(t)

estimated by ridge regression on finite-difference log-growth rates, and
forecast by integrating from a held-out subject's first sample.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

DIR = Path(__file__).resolve().parents[2] / "data" / "raw" / "mdsine2"


def load_absolute(top_n: int = 40) -> tuple[dict[int, pd.DataFrame], pd.DataFrame, list[str]]:
    counts = pd.read_csv(DIR / "counts.tsv", sep="\t", index_col=0)
    meta = pd.read_csv(DIR / "metadata.tsv", sep="\t").set_index("sampleID")
    qpcr = pd.read_csv(DIR / "qpcr.tsv", sep="\t", index_col=0)
    pert = pd.read_csv(DIR / "perturbations.tsv", sep="\t")
    samples = [s for s in counts.columns if s in meta.index and s in qpcr.index]
    rel = counts[samples] / counts[samples].sum(0)
    taxa = rel.mean(1).sort_values(ascending=False).index[:top_n].tolist()
    total = qpcr.loc[samples].mean(1)  # geometric mean would also work; replicate mean kept
    absb = rel.loc[taxa] * total.values
    subjects = {}
    for subj, grp in meta.loc[samples].groupby("subject"):
        if not str(subj).isdigit():
            continue  # e.g. inoculum rows
        df = absb[grp.index].T
        df.index = grp["time"].values
        subjects[int(subj)] = df.sort_index()
    return subjects, pert, taxa


def perturbation_matrix(times: np.ndarray, pert: pd.DataFrame, subject: int, names: list[str]) -> np.ndarray:
    U = np.zeros((len(times), len(names)))
    for _, row in pert[pert.subject == subject].iterrows():
        k = names.index(row["name"])
        U[:, k] = ((times >= row["start"]) & (times <= row["end"])).astype(float)
    return U


def design(subjects, pert, names, subj_ids, eps=1e5):
    X, Y = [], []
    for s in subj_ids:
        df = subjects[s]; t = df.index.values.astype(float); x = df.values + eps
        U = perturbation_matrix(t, pert, s, names)
        for k in range(len(t) - 1):
            dt = t[k + 1] - t[k]
            if dt <= 0:
                continue
            Y.append((np.log(x[k + 1]) - np.log(x[k])) / dt)
            X.append(np.concatenate([[1.0], x[k] / 1e10, U[k]]))
    return np.array(X), np.array(Y)


def fit_glv(X, Y, lam=1.0):
    """Ridge: W = (X^T X + lam I)^-1 X^T Y, intercept unpenalised."""
    P = np.eye(X.shape[1]) * lam; P[0, 0] = 0.0
    return np.linalg.solve(X.T @ X + P, X.T @ Y)


def forecast(W, x0, times, U, n_taxa, eps=1e5, substeps=20):
    x = x0 + eps; out = [x.copy()]
    for k in range(len(times) - 1):
        dt = (times[k + 1] - times[k]) / substeps
        for _ in range(substeps):
            feat = np.concatenate([[1.0], x / 1e10, U[k]])
            g = np.clip(feat @ W, -5, 5)
            x = np.clip(x * np.exp(g * dt), 1.0, 1e13)
        out.append(x.copy())
    return np.array(out)
