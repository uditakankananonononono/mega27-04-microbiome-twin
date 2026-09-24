"""Population-trajectory forecaster for held-out-subject microbiome forecasting.

For held-out subject s, taxon i, time t (training subjects O):
  mu_i(t)   = mean_{o in O, x_oi(t) > 0} log10 x_oi(t)          (presence-conditional)
  m_i(t)    = mean_{o in O} log10(x_oi(t) + eps)                  (unconditional)
  pred(t)   = mu_i(t) + w(t) [ log10 x_si(t0) - mu_i(t0) ],   w(t) = exp(-(t - t0)/tau)
tau is chosen by inner leave-one-subject-out on the training subjects only.
Only the held-out subject's initial timepoint is used, as in the MDSINE2 benchmark.
"""
from __future__ import annotations

import numpy as np


def interp_logs(days_o, vals_o, days, eps, conditional):
    lv = np.log10(np.asarray(vals_o) + eps)
    if not conditional:
        return np.interp(days, days_o, lv), np.ones(len(days), bool)
    pos = np.asarray(vals_o) > 0
    if pos.sum() == 0:
        return np.full(len(days), np.nan), np.zeros(len(days), bool)
    # presence mask interpolated by nearest sample
    idx = np.clip(np.searchsorted(days_o, days), 0, len(days_o) - 1)
    return np.interp(days, np.asarray(days_o)[pos], np.log10(np.asarray(vals_o)[pos])), pos[idx]


def population_curve(train, days, eps=1e3, conditional=True):
    """train: list of (days_o, vals_o). Returns log10 curve on `days`."""
    cur, msk = zip(*[interp_logs(d, v, days, eps, conditional) for d, v in train])
    cur = np.array(cur); msk = np.array(msk)
    if conditional:
        w = msk.astype(float)
        num = np.nansum(np.where(msk, cur, 0), 0); den = w.sum(0)
        fallback = np.nanmean(np.array([interp_logs(d, v, days, eps, False)[0] for d, v in train]), 0)
        out = np.where(den > 0, num / np.maximum(den, 1), fallback)
        return out
    return cur.mean(0)


def forecast(train, days, x0, tau, eps=1e3, conditional=True):
    mu = population_curve(train, days, eps, conditional)
    w = np.exp(-(days - days[0]) / tau) if tau > 0 else np.zeros(len(days))
    return mu + w * (np.log10(x0 + eps) - mu[0])
