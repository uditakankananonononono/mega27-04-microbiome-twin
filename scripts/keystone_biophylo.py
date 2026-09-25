"""Bio.Phylo oral clustering on OTOL topology; preregistration_biophylo.md."""
import json, re
import numpy as np, pandas as pd
from Bio import Phylo
from scipy.sparse.csgraph import shortest_path
from scipy.sparse import lil_matrix
from keystone_methodgeneral import ORAL


def main():
    T=Phylo.read('data/otol/induced.tre','newick')
    nodes=list(T.find_clades()); idx={id(n):i for i,n in enumerate(nodes)}
    A=lil_matrix((len(nodes),len(nodes)),dtype=float)
    for p in nodes:
        for c in p.clades: A[idx[id(p)],idx[id(c)]]=A[idx[id(c)],idx[id(p)]]=1
    K=pd.read_csv('results/keystone_kegg_genus.csv').dropna(subset=['GAI']).drop_duplicates('genus_clean')
    rr=json.load(open('data/otol/tnrs.json')); ott={}
    for r in rr:
        m=[x for x in r['matches'] if x['taxon'].get('rank')=='genus']
        if m: ott[r['name']]=m[0]['taxon']['ott_id']
    ids={int(t.name[3:]):idx[id(t)] for t in T.get_terminals() if t.name and re.fullmatch(r'ott\d+',t.name)}
    K=K[K.genus_clean.map(ott).isin(ids)].copy()
    tips=np.array([ids[ott[g]] for g in K.genus_clean]); oral=np.array([g in ORAL for g in K.genus_clean]); D=shortest_path(A.tocsr(),directed=False,unweighted=True)[np.ix_(tips,tips)]
    def mean(mask):
        d=D[np.ix_(mask,mask)]; return float(d[np.triu_indices(len(d),1)].mean())
    obs=mean(np.flatnonzero(oral)); rng=np.random.default_rng(39)
    null=np.array([mean(rng.choice(len(K),int(oral.sum()),replace=False)) for _ in range(1000)])
    J={'tool':'Biopython Bio.Phylo (synthetic-tree topology)','n_tips':len(K),'n_oral':int(oral.sum()),'mean_oral_distance':obs,'null_mean':float(null.mean()),'p_one_sided':float((1+(null<=obs).sum())/1001),'G1_pass':bool(len(K)>=100 and oral.sum()>=20)}
    J['BP1_pass']=bool(J['G1_pass'] and J['p_one_sided']<0.05)
    with open('results/keystone_biophylo.json','w') as out: json.dump(J,out,indent=1)
    print(json.dumps(J))
if __name__=='__main__': main()
