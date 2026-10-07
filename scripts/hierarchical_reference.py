"""Separate analytic normal-model reference, not a new method."""
import itertools,json,time
import numpy as np
from scipy.stats import t,norm
from hierarchical_precision import interval_mean


def reference_intervals(means, variance):
    x=np.asarray(means,float);n=len(x);mean=x.mean()
    tw=t.ppf(.975,n-1)*x.std(ddof=1)/np.sqrt(n)
    zw=norm.ppf(.975)*np.sqrt(variance/n)
    return {'student_t':np.array([mean-tw,mean+tw]),'known_variance_oracle':np.array([mean-zw,mean+zw])}


def run():
    start=time.monotonic();rng=np.random.default_rng(20261008);rows=[]
    for n,m,rho in itertools.product([4,5,10,20],[1,25],[0.,.5,.9]):
        records={k:[] for k in ['cluster','student_t','known_variance_oracle']}
        for _ in range(500):
            data=np.sqrt(rho)*rng.normal(size=(n,1))+np.sqrt(1-rho)*rng.normal(size=(n,m))
            means=data.mean(1)
            intervals=reference_intervals(means,rho+(1-rho)/m)
            intervals['cluster']=interval_mean(means,rng)
            for name,(lo,hi) in intervals.items():records[name].append([lo<=0<=hi,lo>0,hi-lo])
        row={'subjects':n,'repeats':m,'rho':rho,'true_gap':0.,'mc_panels':500}
        for name,rec in records.items():
            a=np.array(rec,float);p=float(a[:,0].mean())
            row[name]={'coverage':p,'positive_exclusion_rate':float(a[:,1].mean()),'mean_width':float(a[:,2].mean()),'coverage_mc_se':float(np.sqrt(p*(1-p)/500))}
        rows.append(row)
    return {'scope':'independent normal equal-repeat subject means only; oracle knows variance; no biology or new method','seed':20261008,'bootstrap_draws':199,'cells':rows,'cell_count':24,'panels':12000,'intervals':36000,'runtime_seconds':time.monotonic()-start,'useful_win':False}

if __name__=='__main__':print(json.dumps(run(),indent=2))
