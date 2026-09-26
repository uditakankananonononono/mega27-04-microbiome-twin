"""Reproducibility manifest for model runs, without hiding missing evidence."""
from __future__ import annotations

import hashlib
from pathlib import Path


def hash_files(paths):
    result={}
    for path in paths:
        p=Path(path)
        if not p.is_file():raise ValueError(f"not a file: {p}")
        h=hashlib.sha256()
        with p.open('rb') as f:
            for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
        result[str(p)]=h.hexdigest()
    return result


def run_record(*, code_commit, protocol_file, source_files, train_ids, test_ids, seed, model_name):
    """Materialize identifiers and hashes before a new model attempt."""
    tr=set(train_ids);te=set(test_ids)
    if not code_commit or not model_name or not tr or not te or tr & te:
        raise ValueError("code/model and disjoint nonempty train/test IDs required")
    if not isinstance(seed,int):raise ValueError("integer seed required")
    return {"code_commit":code_commit,"protocol_hash":hash_files([protocol_file]),
            "source_hashes":hash_files(source_files), "train_ids":sorted(tr),
            "test_ids":sorted(te),"seed":seed,"model_name":model_name,
            "status":"pre_run_manifest_not_a_result"}
