"""Conservative genus mapping for a fixed EMP BIOM taxonomy.

A genus string can occur under distinct higher ranks. It is not a unique
biological feature in that case; exclude it from cross-source genus matching.
"""
from __future__ import annotations

from collections import defaultdict


def unambiguous_genus_mapping(taxonomy):
    """Return feature-to-genus labels and names with conflicting parent paths.

    Input is a sequence of seven-rank taxonomy rows (strings or bytes). The
    first six ranks are kingdom through genus. Unnamed genera are excluded.
    """
    prefixes = ("k__", "p__", "c__", "o__", "f__", "g__")
    decoded = []
    parents = defaultdict(set)
    for row in taxonomy:
        if len(row) < 6:
            raise ValueError("taxonomy row has fewer than six ranks")
        levels = tuple(v.decode() if isinstance(v, bytes) else str(v) for v in row[:6])
        genus = levels[5].removeprefix("g__").strip()
        if not genus or genus.lower() in ("uncultured", "unclassified"):
            decoded.append(None)
            continue
        parent = tuple(v.removeprefix(prefix).strip() for v, prefix in zip(levels[:5], prefixes))
        parents[genus].add(parent)
        decoded.append(genus)
    ambiguous = {genus for genus, paths in parents.items() if len(paths) > 1}
    return [genus if genus not in ambiguous else None for genus in decoded], ambiguous
