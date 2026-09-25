"""Pre-registered family-deletion sensitivity; see results/preregistration_oral_lfo.md."""
import json, sys
import pandas as pd
sys.path.insert(0, 'scripts')
import keystone_methodgeneral as mg


def families():
    T = pd.read_csv('data/ref/HOMD_taxon_table_v4.2.csv', sep='\t', skiprows=1, dtype=str)
    T = T[T['Body Site(s)'].str.contains('oral', case=False, na=False)]
    F = T[['Genus', 'Family']].dropna().sort_values(['Genus', 'Family']).drop_duplicates('Genus')
    K = set(pd.read_csv('results/keystone_kegg_genus.csv').dropna(subset=['GAI']).genus_clean)
    F = F[F.Genus.isin(K)]
    counts = F.groupby('Family').Genus.nunique()
    return {f: sorted(F.loc[F.Family.eq(f), 'Genus'].tolist()) for f in sorted(counts[counts >= 2].index)}


def labels(path):
    L = pd.read_csv(path).dropna(subset=['genus'])
    return L.assign(top=mg.truthy(L.top_gl))[['study','genus','top']]


def main():
    fs = families(); files = {'gglasso':'results/keystone_gglasso_per_study.csv.gz','igraph':'results/keystone_igraph_per_study.csv.gz'}
    J = {'eligible_families': fs, 'baseline':{}, 'deleted':{}}
    for method, path in files.items():
        L = labels(path); J['baseline'][method] = mg.fit(L)
        for family, genera in fs.items():
            J['deleted'].setdefault(family,{})[method] = mg.fit(L.loc[~L.genus.isin(genera)])
    J['G1_pass'] = len(fs)>=3
    J['LFO1_pass'] = J['G1_pass'] and all(r['coef_oral']>0 and r['p_oral']<0.05 for f in fs for r in J['deleted'][f].values())
    with open('results/keystone_oral_lfo.json','w') as out: json.dump(J,out,indent=1)
    print(json.dumps(J))

if __name__ == '__main__': main()
