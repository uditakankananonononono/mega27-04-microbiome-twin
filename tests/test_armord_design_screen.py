import hashlib
import zipfile
import pytest
from scripts.armord_design_screen import screen,PREFIX

def test_design_screen_reads_no_taxa(tmp_path):
    archive=tmp_path/'a.zip'
    with zipfile.ZipFile(archive,'w') as z:
        z.writestr(PREFIX+'Samples.csv','pid,samp_id,collected_days_after_first_sample\np1,s1,0\np1,s2,8\np2,s3,0\n')
        z.writestr(PREFIX+'Patients.csv','pid,category,private\np1,Haem_autograft,SECRET\np2,Medical,PRIVATE\n')
        z.writestr(PREFIX+'Antimicrobial_exposures.csv','pid,firstdose_days_after_first_sample,lastdose_days_after_first_sample,drug\np1,2,5,SECRET\np1,2,5,SECRET\np2,bad,5,SECRET\n')
        z.writestr(PREFIX+'Taxa_Metaphlan.csv','samp_id,perc\ns1,TOP_SECRET\n')
    result=screen(archive,hashlib.sha256(archive.read_bytes()).hexdigest())
    assert result['prepost_exposure_rows']==2 and result['duplicate_person_interval_coordinates']==1
    assert result['unparseable_exposure_time_rows']==1 and 'SECRET' not in str(result)
    with pytest.raises(ValueError,match='checksum'):screen(archive,'0'*64)
