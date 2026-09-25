"""Anaerobe-keystone PGLS on the Open Tree of Life synthetic tree (pre-registered: results/preregistration_otol.md).
Fetches TNRS matches and the induced subtree from api.opentreeoflife.org (v3); caches to data/otol/.
Grafen branch lengths; Brownian covariance; Pagel lambda by grid ML; GLS frac_top ~ GAI. Output results/keystone_otol.json."""
import json, os, re, sys, urllib.request
import numpy as np, pandas as pd, statsmodels.api as sm
from scipy.stats import chi2

API = "https://api.opentreeoflife.org/v3"


def post(path, body):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode(), headers={"content-type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=120))


def parse_newick(s):
    """Minimal Newick parser -> (parent list, label list). Branch lengths ignored."""
    s = s.strip().rstrip(";"); parent, label, stack = [], [], []; last = -1; closed = False; i = 0
    def new(p): parent.append(p); label.append(""); return len(parent) - 1
    while i < len(s):
        c = s[i]
        if c == "(": stack.append(new(stack[-1] if stack else -1)); closed = False; i += 1
        elif c == ",": closed = False; i += 1
        elif c == ")": last = stack.pop(); closed = True; i += 1
        else:
            j = i
            while j < len(s) and s[j] not in "(),": j += 1
            tok = s[i:j].split(":")[0].strip("'"); node = last if closed else new(stack[-1] if stack else -1)
            label[node] = tok; closed = False; i = j
    return parent, label


def grafen_cov(parent, tips):
    """Grafen heights (n_desc_tips - 1, root scaled to 1); V_ij = root height - height of LCA."""
    n = len(parent); kids = [[] for _ in range(n)]
    for k, p in enumerate(parent):
        if p >= 0: kids[p].append(k)
    ntip = [0] * n
    for k in range(n - 1, -1, -1):
        ntip[k] = 1 if not kids[k] else sum(ntip[c] for c in kids[k])
    root = parent.index(-1); h = np.array([t - 1 for t in ntip], float) / (ntip[root] - 1)
    def path(k):
        out = []
        while k != -1: out.append(k); k = parent[k]
        return out
    P = [path(t) for t in tips]; m = len(tips); V = np.zeros((m, m))
    for a in range(m):
        sa = set(P[a])
        for b in range(a, m):
            lca = next(x for x in P[b] if x in sa); V[a, b] = V[b, a] = 1.0 - h[lca]
    return V


def gls(y, X, V, lam):
    W = lam * V + (1 - lam) * np.diag(np.diag(V)); L = np.linalg.cholesky(W); Li = np.linalg.inv(L)
    r = sm.OLS(Li @ y, Li @ X).fit(); e = Li @ y - Li @ X @ r.params; n = len(y); s2 = e @ e / n
    return -0.5 * (n * np.log(2 * np.pi * s2) + 2 * np.log(np.diag(L)).sum() + n), r


def main(out="results/keystone_otol.json"):
    os.makedirs("data/otol", exist_ok=True)
    K = pd.read_csv("results/keystone_kegg_genus.csv").dropna(subset=["GAI"]).drop_duplicates("genus_clean").reset_index(drop=True)
    mf = "data/otol/tnrs.json"
    if not os.path.exists(mf):
        res = []
        for i in range(0, len(K), 100):
            res += post("/tnrs/match_names", {"names": K.genus_clean[i:i + 100].tolist(), "do_approximate_matching": False, "context_name": "Bacteria"})["results"]
        json.dump(res, open(mf, "w"))
    ott = {}
    for r in json.load(open(mf)):
        ms = [m for m in r["matches"] if m["taxon"].get("rank") == "genus"]
        if ms: ott[r["name"]] = ms[0]["taxon"]["ott_id"]
    tf = "data/otol/induced.tre"
    if not os.path.exists(tf):
        ids = sorted(set(ott.values())); body = {"ott_ids": ids, "label_format": "id"}
        try:
            nw = post("/tree_of_life/induced_subtree", body)["newick"]
        except urllib.error.HTTPError as e:
            bad = json.loads(e.read()).get("unknown", {}); drop = {int(re.sub(r"\D", "", k)) for k in bad}
            body["ott_ids"] = [x for x in ids if x not in drop]; nw = post("/tree_of_life/induced_subtree", body)["newick"]
        open(tf, "w").write(nw)
    parent, label = parse_newick(open(tf).read())
    tipnode = {int(l[3:]): k for k, l in enumerate(label) if re.fullmatch(r"ott\d+", l)}
    K = K[K.genus_clean.map(ott).isin(tipnode)].reset_index(drop=True)
    V = grafen_cov(parent, [tipnode[ott[g]] for g in K.genus_clean])
    grid = np.round(np.arange(0, 1.0001, 0.05), 2); y = K.frac_top.values
    ll0 = [gls(y, np.ones((len(y), 1)), V, l)[0] for l in grid]
    X = sm.add_constant(K.GAI.values); ll = [gls(y, X, V, l)[0] for l in grid]; lm = float(grid[int(np.argmax(ll))])
    _, rb = gls(y, X, V, 1.0); _, rm = gls(y, X, V, lm)
    J = {"tool": "Open Tree of Life API v3 (TNRS + induced synthetic subtree)", "n_input": int(len(pd.read_csv("results/keystone_kegg_genus.csv").dropna(subset=["GAI"]).drop_duplicates("genus_clean"))),
         "n_matched_ott": len(ott), "n_on_tree": int(len(K)), "G1_pass": bool(len(K) >= 150),
         "pagel_lambda_frac_top": {"lambda_ml": float(grid[int(np.argmax(ll0))]), "LR_vs_0_p": float(chi2.sf(2 * (max(ll0) - ll0[0]), 1))},
         "brownian": {"slope": float(rb.params[1]), "p": float(rb.pvalues[1])}, "lambda_ml": lm, "ml": {"slope": float(rm.params[1]), "p": float(rm.pvalues[1])}}
    J["H1_pass"] = bool(J["G1_pass"] and J["brownian"]["slope"] > 0 and J["brownian"]["p"] < 0.05)
    json.dump(J, open(out, "w"), indent=1); print(json.dumps(J))


if __name__ == "__main__":
    main(*sys.argv[1:])
