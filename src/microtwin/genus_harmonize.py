"""Read only terminal genus taxonomic rows, avoiding double-counted hierarchy.

Study-specific abundance tables contain parent phylum/class/family rows and
sometimes species children. Summing all ranks would duplicate reads.
"""
from __future__ import annotations

import re
import numpy as np
import pandas as pd

GENUS = re.compile(r"(?:^|;)g__([^;]+)$")


def terminal_genus(table):
    """Select rows whose final rank is a named genus; preserve sample columns.

    Does not harmonize synonyms across taxonomy versions or claim taxa without
    a genus assignment. Fail closed on collisions instead of silent summation.
    """
    if not isinstance(table, pd.DataFrame) or table.empty or not table.index.is_unique:
        raise ValueError("nonempty unique taxon rows required")
    names = [GENUS.search(str(i)) for i in table.index]
    keep = [i for i, m in enumerate(names) if m and m.group(1).strip() not in ("", "uncultured", "Unclassified")]
    if not keep:
        raise ValueError("no terminal genus rows")
    out = table.iloc[keep].copy()
    out.index = [names[i].group(1).strip() for i in keep]
    if not out.index.is_unique:
        raise ValueError("genus name collision across taxonomic lineages; explicit mapping required")
    x = out.to_numpy()
    if not np.issubdtype(x.dtype, np.number) or not np.isfinite(x).all() or (x < 0).any():
        raise ValueError("nonnegative finite numeric abundances required")
    return out, {"input_taxonomic_rows": len(table), "terminal_genus_rows": len(out),
                 "excluded_non_genus_or_unnamed_rows": len(table) - len(out),
                 "warning": "Unassigned genera excluded; taxonomy version/synonym harmonization remains separate."}
