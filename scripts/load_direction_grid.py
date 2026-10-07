"""Run the frozen eleven-cell deterministic grid, never fetch or fit data."""
import itertools,json,time
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from microtwin.load_direction import bound_absolute_fold


def run():
    start=time.monotonic();cells=[]
    grid=[([.1,.1],[p,p],q) for p,q in itertools.product([.05,.1,.2],[[.9,1.1],[.25,4],[1,1]])]
    grid += [([.08,.12],[.16,.24],[.4,.6]),([.1,.1],[.2,.2],[.5,1])]
    for b,d,q in grid:
        result=bound_absolute_fold(b,d,q,measurement_compatible=True)
        corners=[x*z/y for x,y,z in itertools.product(d,b,q)]
        error=max(abs(result['absolute_fold_bounds'][i]-v) for i,v in enumerate([min(corners),max(corners)]))
        assert error<=1e-12
        cells.append({'before':b,'during':d,'load_ratio':q,'corner_verification_max_error':error,**result})
    return {'cells':cells,'cell_count':len(cells),'seconds':time.monotonic()-start,'useful_win':False,'biological_data':False,'new_method_claim':False}


if __name__=='__main__':
    result=run();Path('results/load_direction_grid_20261007.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'cell_count':result['cell_count'],'seconds':result['seconds'],'statuses':{s:sum(c['status']==s for c in result['cells']) for s in sorted({c['status'] for c in result['cells']})}},indent=2))
