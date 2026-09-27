**2026-09-27 user-verdict revision staged locally:** The positive-result archival audit was revised after Udita supplied her critique. The Drive PDF/DOCX listed here currently remain the previous 70-page sole-author edition until a replacement upload is verified.

**Replacement verified (2026-09-27):** The same Drive IDs now contain the 70-page PDF bearing only Udita Phookan as author and corresponding DOCX, both re-downloaded and byte-verified. The old 71-page checksums in the historical table below identify the previous versions, not the current files. Current PDF SHA-256 `ab0a16ff0772a0015c3d01be1b0d27fc073a0da246f419f61dcf5328688a8eb9`; current DOCX SHA-256 `8057a1317562fe7979e61fbe9755959eafa336debc3e7b17ec55a1fd8c66407e`.

# Drive delivery - MEGA27 item 4 (microbiome digital twin)

Uploaded to Drive folder 1D-yJqoTmmIb9EvrTHN0LiVYfZIajKGeP on 26 Sep 2026.
All files byte-verified by re-download (SHA-256 matches below). v3: final - includes the
complete 6/6 ConstStack (graphtwin2b) matrix (Soil_Vivo landed 11:46 IST, tie vs glv).

## Current files

| File | Drive ID | SHA-256 |
|---|---|---|
| mega27-04-microbiome-twin-paper.pdf (71 pp, final) | 1nYCjg7J-f7FtvT6OzC-U8doXOnpUYbAi | db70a3c2d71feae54a66ce8eb60b418ae3b7907875e1aef1ed70bf926498d3b2 |
| mega27-04-microbiome-twin-paper.docx (editable) | 1PWwLHXIBj2YvjgxR-8OT7HaTpS6MwI5T | d474a93911e5e6f88380c89a6572e156edfa3087e87ebee1f8b8c92f95f2c7b1 |
| mega27-04-microbiome-twin.bundle.part_00 | 1ZdPzcn658CimBWE545EVp8aiav3Ei4bD | 69183df2437c9e187d4decccacd12c2a4f12269fb7e76d2dae04f67f3e902f9a |
| mega27-04-microbiome-twin.bundle.part_01 | 1jD1svXqpZB6v4V6ysLt2f1XKiAJra_kg | 25e5da4a628aa6b033a5d8249d526974cf8a35caca9596db8f1a76a1d4884a44 |
| mega27-04-microbiome-twin.bundle.part_02 | 14STy50gRwhgKZctKwXtj1VEuFy52emDY | ecc6d986bc7c085582892e569fbb7c8e379a1dc428cc79d277f69e7fce82091b |

The git bundle exceeded the 25 MB upload limit, so it was split. Reassemble:

    cat mega27-04-microbiome-twin.bundle.part_00 mega27-04-microbiome-twin.bundle.part_01 mega27-04-microbiome-twin.bundle.part_02 > mega27-04-microbiome-twin.bundle
    # expected SHA-256: 78eadd31e282e03358f0e092c6af56d25ba610d2ebd3b992389ce38aa8ce2982
    git clone mega27-04-microbiome-twin.bundle mega27-04-microbiome-twin

Bundle HEAD: cd7038c (all ISEF judge-loop fixes Rounds 1-3, corrected verbatim Round 3
record, complete 6/6 ConstStack matrix). Reassembled bundle passes git bundle verify.

## Superseded (renamed with SUPERSEDED prefix in the folder)

- v1 bundle pair (HEAD e8c4181): predated the Round 3 verbatim-question record fix.
- v2 paper PDF/DOCX + bundle pair (HEAD 099daf0): predated the final Soil_Vivo ConstStack cell.
  Paper content difference between v2 and v3: the stacking tables now include the sixth
  Soil_Vivo ConstStack row (tie vs glv, diff +0.00001, CI [-0.0004, +0.0002]).
