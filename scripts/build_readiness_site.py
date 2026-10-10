"""Allowlisted byte-exact public site build, no source/private outcome paths."""
import hashlib,json,shutil,subprocess,runpy,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PYTHON=['__init__.py','admission_boundary.py','admission_evidence_bundle.py','nested_perturbation_design.py','specimen_lineage.py','censor_contract.py','comparator_capability.py','source_readiness.py','admission_demo.py']
ASSETS=['OMM12_OUTCOME_ADMISSION_PROPOSAL_20261010.md','OMM12_DOCUMENTARY_CLOSEOUT_20261010.md','omm12_quarantine_certificate_20261010.json','omm12_platform_boundary_check_20261010.json','omm12_admission_evidence_receipt_20261010.json','omm12_nested_design_metadata_20261010.json','omm12_specimen_lineage_metadata_20261010.json','omm12_censor_semantics_metadata_20261010.json','omm12_comparator_plan_metadata_20261010.json','omm12_integrated_readiness_20261010.json','readiness_inputs.json']
RUNTIME=['pyodide.mjs','pyodide.asm.mjs','pyodide.asm.wasm','python_stdlib.zip','pyodide-lock.json','LICENSE.pyodide','LICENSE.python','SOURCE_NOTICE.txt']

def build():
    from microtwin.admission_demo import create_demo
    from microtwin.admission_evidence_bundle import create_receipt
    out=ROOT/'docs/readiness';out.mkdir(parents=True,exist_ok=True)
    allowed={};origins={}
    def copy(src,dest):
        target=out/dest;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,target);origins[dest]=str(src.relative_to(ROOT))
    for n in ['index.html','style.css','app.js']:copy(ROOT/'web/readiness'/n,n)
    for n in PYTHON:copy(ROOT/'src/microtwin'/n,'python/microtwin/'+n)
    for n in ASSETS:copy(ROOT/'results'/n,'assets/'+n)
    with tempfile.TemporaryDirectory() as t:
        base=Path(t)/'synthetic';create_demo(base);config=json.loads((ROOT/'results/readiness_inputs.json').read_text())
        for role,n in [('design','test_nested_perturbation_design.py'),('lineage','test_specimen_lineage.py'),('semantics','test_censor_contract.py'),('fairness','test_comparator_capability.py')]:
            obj=runpy.run_path(str(ROOT/'tests'/n))['fixture']();(base/config['roles'][role]).write_text(json.dumps(obj))
        (base/'readiness_inputs.json').write_text(json.dumps(config));create_receipt(base/config['roles']['evidence_receipt'],evidence_dir=base)
        for p in base.iterdir():
            dest=out/'synthetic'/p.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest);origins['synthetic/'+p.name]='synthetic-test-fixture-not-source'
    for n in RUNTIME:origins['runtime/'+n]='pinned-Pyodide-314.0.7'
    for p in out.rglob('*'):
        if p.is_file() and p.name!='asset-manifest.json':
            rel=str(p.relative_to(out))
            if rel not in origins:raise ValueError('nonallowlisted site artifact')
            b=p.read_bytes();allowed[rel]={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'origin':origins[rel]}
    manifest={'base_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'runtime_version':'314.0.7','total_bytes':sum(x['bytes'] for x in allowed.values()),'files':allowed,'note':'Unsigned byte identity only, not permission/scientific authenticity. Public metadata and synthetic fixtures only.'}
    (out/'asset-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest
if __name__=='__main__':print(json.dumps({k:v for k,v in build().items() if k!='files'}))
