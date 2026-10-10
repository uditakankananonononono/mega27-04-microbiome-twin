"""Exact caller-submitted labels, not proof of distinct biological people."""
import csv,hashlib,io
from pathlib import Path

def parse_subject_records(raw):
    """Strict logical records without echoing private decoding/parser details."""
    try:
        return list(csv.reader(io.StringIO(raw.decode('utf-8')), strict=True))
    except (UnicodeError, csv.Error) as exc:
        raise ValueError('subject map must contain valid UTF-8 and well-formed CSV records') from exc


def check_two_maps(train_map,query_map,train_ids,query_ids):
    subjects=[];hashes=[]
    for path,ids in [(train_map,train_ids),(query_map,query_ids)]:
        p=Path(path)
        if not p.is_file() or p.stat().st_size>50_000_000:raise ValueError('missing or oversized subject map')
        raw=p.read_bytes();rows=parse_subject_records(raw)
        if not rows or rows[0]!=['sample_id','subject_id'] or len(rows)!=len(ids)+1 or any(len(r)!=2 for r in rows[1:]):raise ValueError('subject map exact header/row coverage required')
        sample=[r[0] for r in rows[1:]];labels=[r[1] for r in rows[1:]]
        if any(not v or v!=v.strip() for v in sample+labels) or len(set(sample))!=len(sample) or set(sample)!=set(ids):raise ValueError('subject map exact nonempty partition labels required')
        subjects.append(set(labels));hashes.append(hashlib.sha256(raw).hexdigest())
    if subjects[0]&subjects[1]:raise ValueError('subject crosses train/query partitions')
    return hashes
