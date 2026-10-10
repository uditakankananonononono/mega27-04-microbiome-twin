"""Frozen Stage A/B only. Raw outcomes never enter the public certificate."""
import hashlib
import io
import json
import math
import os
import re
import zipfile
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET

HASH='45157de4fd55eacdaf662785d376b170f6d8711984d4ab777635f61fe7d6d81a'
MEMBER='source-data_table_1_revision.xlsx'
TOKENS=['KB1','YL2','KB18','YL27','YL31','YL32','YL44','YL45','I46','I48','I49','YL58']
LABEL=re.compile(r'^(OMM12|OMM11-(KB1|YL2|KB18|YL27|YL31|YL32|YL44|YL45|I46|I48|I49|YL58))_E[123]_(AF|APF)_W[123]$')
NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
ROOT=Path(__file__).resolve().parents[1]


def classification(kind, literal, formula=False):
    if formula:
        return 'REJECT_FORMULA'
    if literal is None:
        return 'AMBIGUOUS_MISSING'
    if kind=='e':
        return 'LITERAL_ERROR'
    if kind in ('s','inlineStr','str'):
        return 'LITERAL_FLAG' if literal in ('NA','N/A','', '/') else 'REJECT_UNEXPECTED_TEXT'
    if kind not in ('n',None):
        return 'REJECT_TYPE'
    try:
        value=float(literal)
    except (ValueError,TypeError):
        return 'REJECT_NUMERIC_PARSE'
    if not math.isfinite(value) or value<0:
        return 'REJECT_NONFINITE_OR_NEGATIVE'
    return 'AMBIGUOUS_ZERO' if value==0 else 'NUMERIC_REPRESENTATION_VALID'


def require_allowed(address,manifest):
    if address not in manifest:
        raise ValueError('OFF_MANIFEST_ACCESS_REFUSED')


def run(source,private_path):
    raw=Path(source).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=HASH:
        raise ValueError('SOURCE_HASH_MISMATCH')
    outer=zipfile.ZipFile(io.BytesIO(raw))
    inner=zipfile.ZipFile(io.BytesIO(outer.read(MEMBER)))
    strings=[]
    sr=ET.fromstring(inner.read('xl/sharedStrings.xml'))
    for si in sr.findall('s:si',NS):
        strings.append(''.join(t.text or '' for t in si.findall('.//s:t',NS)))
    # Text-only rights review across shared string table/properties/comments.
    pattern=re.compile(r'copyright|licen[cs]e|\brights\b|creative.?commons|\bCC.BY\b|permission',re.I)
    rights=[]
    for text in strings:
        if pattern.search(text):rights.append('SHARED_STRING_RIGHTS_NOTE')
    for name in inner.namelist():
        if name.startswith('docProps/') or 'comment' in name.lower():
            text=' '.join(ET.fromstring(inner.read(name)).itertext())
            if pattern.search(text):rights.append('PROPERTY_OR_COMMENT_RIGHTS_NOTE')
    if rights:raise ValueError('RIGHTS_REVIEW_REQUIRED_BEFORE_NUMERIC_ACCESS')
    workbook=ET.fromstring(inner.read('xl/workbook.xml'))
    sheets=workbook.find('s:sheets',NS)
    tab=next((s for s in sheets if s.attrib['name']=='Tab1'),None)
    if tab is None:raise ValueError('SHEET_MISSING')
    rid=tab.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
    rels=ET.fromstring(inner.read('xl/_rels/workbook.xml.rels'))
    target=next(r.attrib['Target'] for r in rels if r.attrib['Id']==rid)
    path=target.lstrip('/') if target.startswith('/') else 'xl/'+target
    sheet=ET.fromstring(inner.read(path))
    if sheet.find('s:dimension',NS).attrib['ref']!='A1:N229':raise ValueError('DIMENSION_MISMATCH')
    cells={c.attrib['r']:c for c in sheet.findall('s:sheetData/s:row/s:c',NS)}
    def text_cell(address):
        c=cells.get(address)
        if c is None:return None
        if c.attrib.get('t')=='s':return strings[int(c.find('s:v',NS).text)]
        if c.attrib.get('t')=='inlineStr':return ''.join(t.text or '' for t in c.findall('.//s:t',NS))
        raise ValueError('METADATA_NOT_TEXT')
    headers=[text_cell(chr(65+i)+'1') for i in range(14)]
    if headers!=['16Scorr']+TOKENS+['sum']:raise ValueError('HEADER_MISMATCH')
    selected=[];labels=set()
    for row in range(2,230):
        key=text_cell('A'+str(row))
        if key and LABEL.fullmatch(key):
            if key in labels:raise ValueError('DUPLICATE_SAMPLE_KEY')
            labels.add(key);selected.append((row,key))
    expected=json.loads((ROOT/'results/omm12_structural_dictionary_20261010.json').read_text())
    groups=next(g for g in expected['replicate_groups'] if g['sheet']=='Tab1')['groups']
    locked={f"{g['condition']}_E{e}_{g['medium']}_W{w}" for g in groups for e,ws in g['wells_per_experiment'].items() for w in ws}
    if labels!=locked or len(selected)!=222:raise ValueError('LOCKED_LABEL_MISMATCH')
    manifest={chr(col)+str(row) for row,key in selected for col in range(66,78)}
    if len(manifest)!=2664:raise ValueError('MANIFEST_SIZE_MISMATCH')
    cert={'protocol':'OMM12-CULTURE-QPCR-AUDIT-v1','source_sha256':HASH,'source_family':'EXPOSED_CONTROLLED_CULTURE_DEVELOPMENT','stage_A':'PASS','rights':'NO_CONTRARY_TEXT_NOTE_FOUND','selected_rows':222,'allowed_cells':2664,'manifest':[{'sample_key':key,'addresses':[chr(col)+str(row) for col in range(66,78)]} for row,key in selected],'C1':'NOT_ADMITTED_PENDING_PARENT_REVIEW','C2':'BLOCKED','C3':'NOT_PROPOSED','useful_win':'NOT_TESTED'}
    outcomes=[];counter=Counter();issues=[]
    for row,key in selected:
        for col,token in zip(range(66,78),TOKENS):
            address=chr(col)+str(row);require_allowed(address,manifest);c=cells.get(address)
            kind=c.attrib.get('t','n') if c is not None else 'absent'
            v=c.find('s:v',NS) if c is not None else None
            literal=v.text if v is not None else None
            formula=c is not None and c.find('s:f',NS) is not None
            if kind=='s' and literal is not None:literal=strings[int(literal)]
            if kind=='inlineStr':literal=''.join(t.text or '' for t in c.findall('.//s:t',NS))
            status=classification(kind,literal,formula);counter[status]+=1
            outcomes.append({'address':address,'sample_key':key,'strain_token':token,'raw_type':kind,'literal':literal,'status':status})
            if status.startswith('REJECT'):
                issues.append({'address':address,'status':status});break
        if issues:break
    cert['representation_counts']=dict(counter);cert['issues']=issues
    cert['stage_B']='FAIL_STOPPED' if issues else 'QUARANTINE_VALIDATED'
    cert['quantitative_admission']='NOT_ADMITTED'
    private=Path(private_path);private.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    fd=os.open(private,os.O_CREAT|os.O_TRUNC|os.O_WRONLY,0o600)
    with os.fdopen(fd,'w') as f:json.dump({'protocol':cert['protocol'],'source_sha256':HASH,'raw_allowed_cells':outcomes},f)
    return cert

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--private',required=True);p.add_argument('--certificate',required=True);a=p.parse_args()
    cert=run(a.source,a.private);Path(a.certificate).write_text(json.dumps(cert,indent=2)+'\n')
    print(json.dumps({k:v for k,v in cert.items() if k not in ('manifest',)}))
