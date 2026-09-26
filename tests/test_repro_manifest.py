import pytest
from microtwin.repro_manifest import run_record


def test_hashes_and_disjoint_ids(tmp_path):
    p=tmp_path/'protocol';p.write_text('frozen')
    d=tmp_path/'data';d.write_text('bytes')
    r=run_record(code_commit='abc',protocol_file=p,source_files=[d],train_ids=['A'],test_ids=['B'],seed=0,model_name='prior')
    assert r['status']=='pre_run_manifest_not_a_result' and len(next(iter(r['source_hashes'].values())))==64
    with pytest.raises(ValueError):
        run_record(code_commit='abc',protocol_file=p,source_files=[d],train_ids=['A'],test_ids=['A'],seed=0,model_name='prior')
