# Drive delivery - MEGA27 item 4 (microbiome digital twin)

Uploaded to Drive folder 1D-yJqoTmmIb9EvrTHN0LiVYfZIajKGeP on 26 Sep 2026.
All files byte-verified by re-download (SHA-256 matches below).

## Current files

| File | Drive ID | SHA-256 |
|---|---|---|
| mega27-04-microbiome-twin-paper.pdf (71 pp, final) | 184hRZZzQ3arVrq9cnmn43AfbvAmZp81g | e3bbca6fbcbdec1f9c9bccc304582eb4faa330f33b59d97f4e4f86629c1cb8ee |
| mega27-04-microbiome-twin-paper.docx (editable) | 1sH9ejibcF0T-fclsPa3yZepMz6KUq2CA | 8623a0c6e0d7bb5793c9a0dfec55a39a70170b66580a83525afd50b3db3668c3 |
| mega27-04-microbiome-twin.bundle.part_00 | 1C_6_rb-PjNjCYN0rRkILcrYvb6qg1sJw | e372714f38ef002ce10d74354d8af9283c9efe4f7e1b3d2577a7d87d1198b96a |
| mega27-04-microbiome-twin.bundle.part_01 | 15dc5fnoRcU0OcIjm7bTa1x5jYWHAqYzh | 639c0a8ded6ddfd03b566aef31ed4d9a63f47c6ae8f77e10f9eb0343efdd3fe3 |

The git bundle exceeded the 25 MB upload limit, so it was split. Reassemble:

    cat mega27-04-microbiome-twin.bundle.part_00 mega27-04-microbiome-twin.bundle.part_01 > mega27-04-microbiome-twin.bundle
    # expected SHA-256: 8a646f3ebb76b624fcca05bdac11c26b24822bd7ea9ce9f1cccfbacf2a207d5b
    git clone mega27-04-microbiome-twin.bundle mega27-04-microbiome-twin

Bundle HEAD: 099daf0 (includes all ISEF judge-loop fixes, Rounds 1-3, and the corrected
verbatim Round 3 question record). Bundle re-verified after reassembly: git bundle verify passes.

## Superseded

An earlier bundle pair (Drive IDs 1PVNRO_tWWfrQPQni4UufbYQF2owCbwj3, 1CMRctRdTLKogqO1T1Qcx3Zw01CKs0V1Q;
renamed with the SUPERSEDED prefix in the folder, HEAD e8c4181) predates a record-keeping fix to
ISEF_JUDGE_ROUNDS.md (the Round 3 question text had been dropped by a heredoc slip; the judge answer
was always present and byte-identical). Use the current pair above.
