import hashlib
import json

import scripts.harris_metadata_screen as mod


def test_aggregate_screen_uses_no_clinical_rows(tmp_path, monkeypatch):
    sample=tmp_path/'mapping_human_volunteer.txt'
    sample.write_text('#SampleID\tpatient_ID\tday\trandomization_arm\tsample_surviving_dada2\tclinical_note\n'
                      's1\tp1\t0\tDrug\ts1\tprivate\n'
                      's2\tp1\t7\tDrug\ts2\tprivate\n'
                      's3\tp2\t0\tControl\ts3\tprivate\n'
                      's4\tp2\t7\tControl\ts4\tprivate\n')
    monkeypatch.setattr(mod,'SOURCE',sample)
    monkeypatch.setattr(mod,'ROOT',tmp_path)
    monkeypatch.setattr(mod,'EXPECTED',hashlib.sha256(sample.read_bytes()).hexdigest())
    (tmp_path/'results').mkdir()
    mod.main()
    report=(tmp_path/'results/harris_metadata_screen.json').read_text()
    r=json.loads(report)
    assert r['matched_subjects_day_0_7']==2
    assert r['subject_arm_conflicts']==0
    assert 'clinical_note' not in report and 'private' not in report
