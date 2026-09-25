"""SHAP explanation of pre-registered LightGBM model; preregistration_shap.md."""
import json
import numpy as np
import shap
from keystone_boosters import data, model


def main():
    M=data(); features=['GAI','lra','log_ena']; X=M[features].to_numpy(); y=M.frac_top.to_numpy()
    m=model('lightgbm',0); m.fit(X,y)
    V=np.asarray(shap.TreeExplainer(m).shap_values(X))
    mag=np.abs(V).mean(axis=0); signed=V.mean(axis=0); rank=np.argsort(-mag)
    J={'tool':'SHAP TreeExplainer','n_genera':len(M),'G1_pass':bool(len(M)>=180 and V.shape==(len(M),3) and np.isfinite(V).all()),'mean_abs':dict(zip(features,map(float,mag))),'mean_signed':dict(zip(features,map(float,signed))),'ranked_features':[features[i] for i in rank]}
    J['SH1_pass']=bool(J['G1_pass'] and J['ranked_features'][0]=='GAI')
    with open('results/keystone_shap.json','w') as out: json.dump(J,out,indent=1)
    print(json.dumps(J))
if __name__=='__main__': main()
