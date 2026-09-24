"""Benchmark runner: writes results/bench_<dataset>.json incrementally."""
import json, sys, time
import numpy as np
import torch
torch.set_num_threads(1)
sys.path.insert(0, "src")
from microtwin.data import load, CNODE_PUBLISHED_MEDIAN_BC as PUB
from microtwin.evaluate import cross_validate, paired_bootstrap

datasets = sys.argv[1].split(",")
models = sys.argv[2].split(",")
kmax = int(sys.argv[3]) if len(sys.argv) > 3 else 1000
for d in datasets:
    Z, P = load(d); t = time.time()
    k = min(len(Z), kmax)
    e = cross_validate(Z, P, models, k=k)
    out = {"dataset": d, "n": len(Z), "taxa": Z.shape[1], "k": k, "sec": time.time() - t,
           "published_cnode_median": PUB[d],
           "median": {m: float(np.median(v)) for m, v in e.items()},
           "errors": {m: v.tolist() for m, v in e.items()}}
    if "graphtwin" in e and "cnode" in e:
        out["delta_graphtwin_minus_cnode"] = paired_bootstrap(e["graphtwin"], e["cnode"])
    tag = "_".join(models)
    json.dump(out, open(f"results/bench_{d}_{tag}_k{k}.json", "w"))
    print(d, out["n"], k, {m: round(x, 4) for m, x in out["median"].items()}, "pub", PUB[d], round(out["sec"], 1), flush=True)
