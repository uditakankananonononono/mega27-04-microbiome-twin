"""Pre-registered boosted out-of-fold checks; see results/preregistration_boosters.md."""
import json, sys
import numpy as np
from scipy.stats import binomtest
from sklearn.model_selection import KFold
from sklearn.metrics import r2_score
from keystone_xgboost import data


def model(kind, seed):
    if kind == 'lightgbm':
        from lightgbm import LGBMRegressor
        return LGBMRegressor(n_estimators=100,max_depth=2,num_leaves=4,learning_rate=0.03,min_child_samples=15,verbosity=-1,random_state=seed,n_jobs=1)
    from catboost import CatBoostRegressor
    return CatBoostRegressor(iterations=100,depth=2,learning_rate=0.03,l2_leaf_reg=5,verbose=False,random_seed=seed,thread_count=1)


def oof(kind, X, y, seed):
    pred=np.empty(len(y))
    for tr,te in KFold(5,shuffle=True,random_state=seed).split(X):
        m=model(kind,seed); m.fit(X[tr],y[tr]); pred[te]=m.predict(X[te])
    return r2_score(y,pred)


def main(kind):
    M=data(); y=M.frac_top.to_numpy(); X=M[['GAI','lra','log_ena']].to_numpy(); R=X[:,1:]
    pairs=[(oof(kind,X,y,s),oof(kind,R,y,s)) for s in range(20)]
    full=np.array([x[0] for x in pairs]); red=np.array([x[1] for x in pairs]); delta=full-red; n=int((delta>0).sum())
    J={'tool':kind,'n_genera':len(M),'G1_pass':bool(len(M)>=180),'r2_full_mean':float(full.mean()),'r2_reduced_mean':float(red.mean()),'delta_mean':float(delta.mean()),'n_positive':n,'sign_test_p':float(binomtest(n,20).pvalue)}
    J['B1_pass']=bool(J['G1_pass'] and J['r2_full_mean']>0 and J['delta_mean']>0 and n>=15)
    with open(f'results/keystone_{kind}.json','w') as out: json.dump(J,out,indent=1)
    print(json.dumps(J))
if __name__=='__main__': main(sys.argv[1])
