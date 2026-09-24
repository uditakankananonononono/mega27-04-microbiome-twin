"""microtwin command-line tool.

  microtwin audit TABLE [--samples-in-rows] [--k 5] [--min-prev 0.05] [--json OUT]
      Interaction audit on any abundance table (TSV/CSV, optionally .gz). Default layout: taxa x samples
      (MGnify / QIIME style). Reports how much an interaction-aware steady-state model beats the
      presence-conditional prior, with a paired Wilcoxon test.
  microtwin forecast TRAIN_DIR --subject S
      Presence-conditional population forecast for a held-out subject in an MDSINE2-format dataset.
"""
from __future__ import annotations

import argparse, json, sys

import numpy as np
import pandas as pd

from .audit import audit


def _load(path, samples_in_rows):
    sep = "," if path.endswith((".csv", ".csv.gz")) else "\t"
    t = pd.read_csv(path, sep=sep, index_col=0).select_dtypes("number")
    return t if samples_in_rows else t.T


def cmd_audit(a):
    X = _load(a.table, a.samples_in_rows)
    X = X.loc[X.sum(1) > 0]
    prev = (X > 0).mean(0); X = X.loc[:, prev >= a.min_prev]; X = X.loc[X.sum(1) > 0]
    r = audit(X.values, k=a.k, seed=a.seed)
    out = {k: v for k, v in r.items() if k not in ("e_prior", "e_int")}
    verdict = ("interactions add predictive value" if r["wilcoxon_p"] < 0.05 and r["gain"] > 0 else
               "no detectable gain from interactions over the presence prior")
    out["verdict"] = verdict
    print(json.dumps(out, indent=1))
    if a.json: json.dump(r | {"verdict": verdict, "table": a.table}, open(a.json, "w"))
    return 0


def cmd_forecast(a):
    from .popforecast import forecast
    d = pd.read_csv(a.table)
    need = {"subject", "taxon", "day", "abundance"}
    if not need <= set(d.columns): sys.exit(f"table needs columns {sorted(need)}")
    days = np.sort(d[d.subject == a.subject].day.unique())
    rows = []
    for tx, g in d.groupby("taxon"):
        train = [(h.sort_values("day").day.values, h.sort_values("day").abundance.values) for s, h in g.groupby("subject") if s != a.subject]
        x0 = g[(g.subject == a.subject)].sort_values("day").abundance.values
        if not train or len(x0) == 0: continue
        p = forecast(train, days, x0[0], 0, 1e3, True)
        rows += [{"taxon": tx, "day": dd, "pred_log10": float(v)} for dd, v in zip(days, p)]
    pd.DataFrame(rows).to_csv(sys.stdout, index=False)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="microtwin")
    sp = ap.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("audit"); a.add_argument("table"); a.add_argument("--samples-in-rows", action="store_true")
    a.add_argument("--k", type=int, default=5); a.add_argument("--min-prev", type=float, default=0.05)
    a.add_argument("--seed", type=int, default=0); a.add_argument("--json"); a.set_defaults(f=cmd_audit)
    f = sp.add_parser("forecast"); f.add_argument("table", help="long CSV: subject,taxon,day,abundance"); f.add_argument("--subject", required=True)
    f.set_defaults(f=cmd_forecast)
    a = ap.parse_args(argv); return a.f(a)


if __name__ == "__main__":
    sys.exit(main())
