"""microtwin command-line tool.

  microtwin audit TABLE [--samples-in-rows] [--k 5] [--min-prev 0.05] [--json OUT]
      Interaction audit on any abundance table (TSV/CSV, optionally .gz). Default layout: taxa x samples
      (MGnify / QIIME style). Reports how much an interaction-aware steady-state model beats the
      presence-conditional prior, with a paired Wilcoxon test.
  microtwin forecast TRAIN_DIR --subject S
  microtwin dependence PAIRED_CSV --group-column study
      Score predictive interaction gain from paired outer-held-out errors; not causal.
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


def cmd_dependence(a):
    from .interaction_score import heldout_scores
    df = pd.read_csv(a.table)
    required = {"sample_id", "prior_error", "interaction_error", a.group_column}
    missing = required - set(df.columns)
    if missing: sys.exit(f"paired loss table missing columns: {sorted(missing)}")
    try:
        result = heldout_scores(df.prior_error.to_numpy(), df.interaction_error.to_numpy(),
                                ids=df.sample_id.tolist(), groups=df[a.group_column].tolist(),
                                n_boot=a.n_boot, seed=a.seed)
    except ValueError as e:
        sys.exit(str(e))
    result["input_file"] = a.table
    result["group_column"] = a.group_column
    print(json.dumps(result, indent=2))
    if a.json:
        with open(a.json, "w") as f: json.dump(result, f, indent=2)
    return 0


def cmd_inspect(a):
    from .research_intake import inspect_local_matrix
    try:
        report = inspect_local_matrix(a.table, unit=a.unit, source_id=a.source_id,
                                      processing_authorized=a.processing_authorized,
                                      subject_map=a.subject_map)
    except ValueError as e:
        sys.exit(str(e))
    print(json.dumps(report, indent=2))
    return 0


def cmd_predict(a):
    from .local_predict import predict_local
    try:
        result, report = predict_local(a.train, a.query, unit=a.unit, source_id=a.source_id,
                                       processing_authorized=a.processing_authorized, subject_map=a.subject_map)
        from pathlib import Path
        dest = Path(a.out)
        if dest.suffix.lower() != '.csv':
            raise ValueError('output path must end in .csv')
        if dest.exists():
            raise ValueError('output file already exists; choose a new path')
        if not dest.parent.is_dir():
            raise ValueError('output parent directory does not exist')
        # Exclusive creation: a second invocation cannot silently overwrite an
        # earlier result or an input file via a same-path race.
        with dest.open('x', newline='') as handle:
            result.to_csv(handle, index=False)
    except ValueError as e:
        sys.exit(str(e))
    report['output_file'] = str(dest)
    print(json.dumps(report, indent=2))
    return 0


def cmd_predict_calibrated(a):
    from .local_calibrated_predict import predict_with_radius
    try:
        result, report = predict_with_radius(a.train, a.calibration, a.query,
                                             unit=a.unit, source_id=a.source_id,
                                             processing_authorized=a.processing_authorized,
                                             subject_map=a.subject_map, calibration_subject_map=a.calibration_subject_map,
                                             query_subject_map=a.query_subject_map, alpha=a.alpha)
        from pathlib import Path
        dest = Path(a.out)
        if dest.suffix.lower() != '.csv':
            raise ValueError('output path must end in .csv')
        if dest.exists():
            raise ValueError('output file already exists; choose a new path')
        if not dest.parent.is_dir():
            raise ValueError('output parent directory does not exist')
        with dest.open('x', newline='') as handle:
            result.to_csv(handle, index=False)
    except ValueError as e:
        sys.exit(str(e))
    report['output_file'] = str(dest)
    print(json.dumps(report, indent=2))
    return 0


def cmd_screen_sources(a):
    """Local bounded metadata screen, never a cohort or rights certificate."""
    from pathlib import Path
    from .source_admission import assess_many
    path = Path(a.matrix)
    try:
        if not path.is_file() or path.stat().st_size > 1_000_000:
            raise ValueError('missing or oversized JSON input (1 MB maximum)')
        with path.open() as f:
            obj=json.load(f)
        if not isinstance(obj,dict) or not isinstance(obj.get('rows'),list) or len(obj['rows'])>1000:
            raise ValueError('JSON needs a rows list of at most 1000 records')
        if type(obj.get('n_studies')) is not int or obj['n_studies'] != len(obj['rows']):
            raise ValueError('n_studies must equal rows length')
        report=assess_many(obj['rows'])
    except (OSError,ValueError,TypeError,json.JSONDecodeError) as e:
        print(f'cannot screen source metadata: {e}',file=sys.stderr)
        return 2
    print(json.dumps(report,indent=2))
    return 0 if report['metadata_ready_for_manual_review'] else 2


def cmd_check_assays(a):
    from pathlib import Path
    from .assay_contract import assess_measurement_contract
    try:
        path=Path(a.contracts)
        if not path.is_file() or path.stat().st_size>1_000_000:
            raise ValueError('missing or oversized contract JSON (1 MB maximum)')
        obj=json.loads(path.read_text())
        if not isinstance(obj,dict) or set(obj)!={'train','query'}:
            raise ValueError('contract JSON requires exactly train and query objects')
        report=assess_measurement_contract(obj['train'],obj['query'])
    except (OSError,ValueError,TypeError) as e:
        print(f'cannot check measurement contracts: {e}',file=sys.stderr)
        return 2
    print(json.dumps(report,indent=2))
    return 0 if report['measurement_fields_match'] else 2


def main(argv=None):
    ap = argparse.ArgumentParser(prog="microtwin")
    sp = ap.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("audit"); a.add_argument("table"); a.add_argument("--samples-in-rows", action="store_true")
    a.add_argument("--k", type=int, default=5); a.add_argument("--min-prev", type=float, default=0.05)
    a.add_argument("--seed", type=int, default=0); a.add_argument("--json"); a.set_defaults(f=cmd_audit)
    f = sp.add_parser("forecast"); f.add_argument("table", help="long CSV: subject,taxon,day,abundance"); f.add_argument("--subject", required=True)
    f.set_defaults(f=cmd_forecast)
    d = sp.add_parser("dependence", help="predictive gain from paired outer-held-out errors")
    d.add_argument("table", help="CSV with sample_id, prior_error, interaction_error and study/group")
    d.add_argument("--group-column", default="study")
    d.add_argument("--n-boot", type=int, default=2000)
    d.add_argument("--seed", type=int, default=0)
    d.add_argument("--json")
    d.set_defaults(f=cmd_dependence)
    i = sp.add_parser("inspect", help="local schema/QC only; no prediction or upload")
    i.add_argument("table", help="samples x taxa TSV/CSV, sample_id first")
    i.add_argument("--unit", choices=("counts","relative_abundance","absolute_abundance"), required=True)
    i.add_argument("--source-id", required=True)
    i.add_argument("--processing-authorized", action="store_true", help="researcher declaration, not proof of rights")
    i.add_argument("--subject-map", help="CSV with sample_id,subject_id for exact grouping check")
    i.set_defaults(f=cmd_inspect)
    p = sp.add_parser("predict", help="local research-only presence-to-composition population baseline")
    p.add_argument("train", help="labeled samples x taxa CSV/TSV; sample_id first")
    p.add_argument("query", help="binary presence matrix, same taxa and order; sample_id first")
    p.add_argument("--unit", choices=("counts","relative_abundance","absolute_abundance"), required=True)
    p.add_argument("--source-id", required=True)
    p.add_argument("--processing-authorized", action="store_true", help="caller declaration, not proof of data rights")
    p.add_argument("--subject-map", help="optional exact sample_id,subject_id CSV for grouping metadata")
    p.add_argument("--out", required=True, help="local CSV path for predicted compositions")
    p.set_defaults(f=cmd_predict)
    c = sp.add_parser('predict-calibrated', help='research-only local population baseline with marginal split-calibrated error radius')
    c.add_argument('train', help='labeled training CSV/TSV')
    c.add_argument('calibration', help='disjoint labeled calibration CSV/TSV')
    c.add_argument('query', help='binary assemblages, disjoint from both')
    c.add_argument('--unit', choices=('counts','relative_abundance','absolute_abundance'), required=True)
    c.add_argument('--source-id', required=True)
    c.add_argument('--processing-authorized', action='store_true', help='caller declaration, not proof of data rights')
    c.add_argument('--subject-map', help='exact train sample_id,subject_id CSV; requires other two maps')
    c.add_argument('--calibration-subject-map', help='exact calibration subject map CSV')
    c.add_argument('--query-subject-map', help='exact query subject map CSV')
    c.add_argument('--alpha', type=float, default=.1)
    c.add_argument('--out', required=True, help='new local CSV path')
    c.set_defaults(f=cmd_predict_calibrated)
    sc = sp.add_parser('screen-sources', help='local metadata-only admission screen; never final benchmark eligibility')
    sc.add_argument('matrix', help='JSON object with n_studies and rows, at most 1 MB/1000 records')
    sc.set_defaults(f=cmd_screen_sources)
    mc=sp.add_parser('check-assays',help='local measurement-contract gate; never certifies source transfer')
    mc.add_argument('contracts',help='JSON with train/query source, material, assay, taxonomy, pipeline and unit')
    mc.set_defaults(f=cmd_check_assays)
    a = ap.parse_args(argv); return a.f(a)


if __name__ == "__main__":
    sys.exit(main())
