"""Does the anaerobe-keystone association survive phylogenetic non-independence?
GTDB r232 bac120 tree (data/gtdb/bac120.tree, parsed with a streaming Newick parser); one representative genome per keystone genus
(first GTDB genome of that genus present as a tip). Brownian covariance V_ij = root-to-LCA path length; Pagel's lambda transform
V(lambda) = lambda*V + (1-lambda)*diag(V), lambda by maximum likelihood (grid). PGLS: frac_top ~ trait (Madin anaerobe; KEGG GAI) via GLS.
Also Pagel's lambda of frac_top alone (phylogenetic signal). Output: results/keystone_pgls.json"""
import gzip, re, json, numpy as np, pandas as pd, statsmodels.api as sm
from scipy.stats import chi2
s = open("data/gtdb/bac120.tree").read().strip().rstrip(";")
parent, blen, label = [], [], []; stack = []; last = -1; after_close = False; i = 0; n = len(s)
def new(p): parent.append(p); blen.append(0.0); label.append(""); return len(parent) - 1
while i < n:
    c = s[i]
    if c == "(": stack.append(new(stack[-1] if stack else -1)); after_close = False; i += 1
    elif c == ",": after_close = False; i += 1
    elif c == ")": last = stack.pop(); after_close = True; i += 1
    else:
        j = i
        while j < n and s[j] not in "(),": j += 1
        tok = s[i:j]; node = last if after_close else new(stack[-1])
        if tok.startswith("'"):
            q = tok.rindex("'"); lab, rest = tok[1:q], tok[q + 1:]; bl = rest[1:] if rest.startswith(":") else ""
        else:
            lab, bl = (tok.rsplit(":", 1) + [""])[:2] if ":" in tok else (tok, "")
        label[node] = lab; blen[node] = float(bl) if bl else 0.0; after_close = False; i = j
parent = np.array(parent); blen = np.array(blen)
tips = {label[k]: k for k in range(len(label)) if label[k].startswith(("RS_", "GB_"))}
tax = {}
with gzip.open("data/gtdb/bac120_tax.tsv.gz", "rt") as f:
    for line in f:
        gid, t = line.rstrip("\n").split("\t"); gen = re.sub(r"_[A-Z]+$", "", t.split(";g__")[1].split(";")[0])
        if gid in tips and gen not in tax: tax[gen] = tips[gid]
K = pd.read_csv("results/keystone_kegg_genus.csv"); K = K[K.genus_clean.isin(tax)].drop_duplicates("genus_clean").reset_index(drop=True)
def anc(k):
    d = {}; path = []
    while k != -1: path.append(k); k = parent[k]
    depth = np.cumsum(blen[path[::-1]]); return dict(zip(path[::-1], depth))
A = [anc(tax[g]) for g in K.genus_clean]; m = len(A); V = np.zeros((m, m))
for a in range(m):
    for b in range(a, m):
        common = A[a].keys() & A[b].keys(); V[a, b] = V[b, a] = max(A[a][x] for x in common) - 0 if a != b else max(A[a].values())
def gls_ll(y, X, lam):
    W = lam * V + (1 - lam) * np.diag(np.diag(V)); L = np.linalg.cholesky(W); Li = np.linalg.inv(L)
    r = sm.OLS(Li @ y, Li @ X).fit(); e = Li @ y - Li @ X @ r.params; nn = len(y); s2 = e @ e / nn
    return -0.5 * (nn * np.log(2 * np.pi * s2) + 2 * np.log(np.diag(L)).sum() + nn), r
grid = np.linspace(0, 1, 21); out = {"n_genera_on_tree": m, "tree_tips": len(tips)}
y = K.frac_top.values; X0 = np.ones((m, 1))
ll = [gls_ll(y, X0, l)[0] for l in grid]; lb = grid[int(np.argmax(ll))]
out["pagel_lambda_frac_top"] = {"lambda_ml": float(lb), "LR_vs_0_p": float(chi2.sf(2 * (max(ll) - ll[0]), 1))}
for tr in ["anaerobe", "GAI"]:
    k = K.dropna(subset=[tr]); idx = k.index.values; Vs = V[np.ix_(idx, idx)]
    Vk, V = V, Vs
    yy = k.frac_top.values; XX = sm.add_constant(k[tr].values)
    lls = [gls_ll(yy, XX, l)[0] for l in grid]; lm = grid[int(np.argmax(lls))]; _, r = gls_ll(yy, XX, lm); _, r1 = gls_ll(yy, XX, 1.0); _, r0 = gls_ll(yy, XX, 0.0)
    out[f"pgls_{tr}"] = {"n": len(k), "lambda_ml": float(lm), "slope_ml": float(r.params[1]), "p_ml": float(r.pvalues[1]), "slope_brownian": float(r1.params[1]), "p_brownian": float(r1.pvalues[1]), "slope_ols": float(r0.params[1]), "p_ols": float(r0.pvalues[1])}
    V = Vk
json.dump(out, open("results/keystone_pgls.json", "w"), indent=1); print(json.dumps(out, indent=1))
