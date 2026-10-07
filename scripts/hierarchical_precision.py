"""Frozen synthetic precision experiment; not real-data power or discovery."""
import itertools,json,time
import numpy as np


def interval_mean(values, rng, draws=199):
    x=np.asarray(values,float)
    ix=rng.integers(len(x),size=(draws,len(x)))
    return np.quantile(x[ix].mean(1),[.025,.975])


def run():
    start=time.monotonic();rng=np.random.default_rng(20261007);rows=[]
    for n,m,rho,delta in itertools.product([4,5,10,20],[1,10,25],[0.,.5,.9],[0.,.25]):
        records={k:[] for k in ['naive','cluster']}
        for _ in range(100):
            data=delta+np.sqrt(rho)*rng.normal(size=(n,1))+np.sqrt(1-rho)*rng.normal(size=(n,m))
            for name,values in [('naive',data.ravel()),('cluster',data.mean(1))]:
                lo,hi=interval_mean(values,rng)
                records[name].append([lo<=delta<=hi,lo>0,hi-lo])
        result={'subjects':n,'repeats':m,'rho':rho,'true_gap':delta,'mc_panels':100}
        for name,rec in records.items():
            a=np.array(rec,float);p=float(a[:,0].mean())
            result[name]={'coverage':p,'positive_exclusion_rate':float(a[:,1].mean()),'mean_width':float(a[:,2].mean()),'coverage_mc_se':float(np.sqrt(p*(1-p)/100))}
        rows.append(result)
    return {'scope':'synthetic known-gap normal equal-repeat percentile bootstrap only; no biological result or universal sample size','seed':20261007,'bootstrap_draws':199,'cells':rows,'cell_count':len(rows),'panels':7200,'intervals':14400,'runtime_seconds':time.monotonic()-start,'useful_win':False}

if __name__=='__main__':
    print(json.dumps(run(),indent=2))
