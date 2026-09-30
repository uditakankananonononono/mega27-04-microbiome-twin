# RR-8 four-sample capacity proposal, September 30, 2026

STATUS: research only, no paid resource provisioned, no raw FASTQ or database download begun. Free institution/HPC capacity first. A four-sample pilot is a feasibility and usable-microbial-depth experiment, not a discovery experiment; it cannot estimate population flight effects. Any paid provisioning needs separate user approval for the account, final price and bounded action.

## Verified inputs

OSD-742 has 145 fecal assays, 290 paired files. Exact compressed bytes: 458,345,112,427 (458.35 decimal GB, 426.87 GiB). NASA raw FastQC reports 1,780,281,767 pairs / 3,560,563,534 reads. Median sample depth 12,046,857 pairs, range 8,625,495–19,358,559. Host contamination estimates range 0.65%–99.81%, median 42.12%. HRremoved filenames refer to human-read removal, not complete mouse-host removal. Do not infer usable microbial reads by treating those files as host-free.

## Pilot selection and outputs

Four terminal 23-day samples: young/old crossed with flight/ground, closest to median read depth in each cell, tie broken by sample label. Selection ignores microbial outcomes. Manifest contains exact eight filenames, bytes and depths. Total 12,011,285,389 compressed bytes and 46,870,787 read pairs. Host estimates 65.48%, 84.85%, 50.72%, 98.45%; this pilot deliberately exposes practical high-host risk but does not cover all dataset depths or biology.

Outputs: integrity/checksum and pairing report; input/QC depth; marker mapping and estimated classified fraction with clear definitions; profile completeness and retained taxa; wall time/MaxRSS per sample; database/software hashes; projected full-run resources with uncertainty. Do not equate marker-mapped reads or estimated classified fraction with directly measured total microbial depth. If reliable usable-microbial-depth estimation needs explicit mouse-genome alignment, return that as an additional resource proposal before adding it. NASA host estimates plus marker-profile coverage are the bounded first approximation.

## Proposed machine and pins

Ubuntu Linux Azure East US Standard_D8s_v5: 8 vCPUs, 32 GiB RAM, 128-GiB Premium SSD P10 scratch (at least 100 GiB), 32-GiB P4 OS disk. One sample at a time. MetaPhlAn 4.2.6 and compatible Bowtie2 version pinned on installation; database mpa_vJan25_CHOCOPhlAnSGB_202503 explicitly pinned, never moving latest. The official database server's latest now resolves to Jan26, so this older stable pin is a reproducibility choice, not a claim it is newest.

Marker archive 5,118,914,560 bytes; prebuilt Bowtie index archive 35,057,633,280 bytes. Download archives sequentially, verify published checksum, extract and delete verified archives before staging pilot reads. Stream compressed FASTQs; avoid uncompressed duplication and large SAM files. Check extracted database footprint and scratch before reads; stop if 128 GiB is inadequate. Published MetaPhlAn documentation states minimum 15 GB RAM for MetaPhlAn 4; 32 GiB is a proposal, not proof that every current database build fits.

## Honest time and cost

Unbenchmarked planning allowance: setup/download 1–3 hours, four sequential profiles 2–5 hours, QC about 30 minutes. Typical planning window 4–8 hours; hard stop at 12 wall-clock hours after resource creation, including setup. If profiles fail or exceed budget, stop and report, do not extend automatically. No claim that profiling speed has been measured on this hardware.

Microsoft live retail API, USD East US Linux on-demand: VM $0.384/hour; P10 disk $19.71/month; P4 OS $5.2795/month; Standard IPv4 public IP $0.005/hour if needed. At the 730-hour monthly approximation, total is $0.42323/hour: $1.69–$3.39 for 4–8 hours, $5.08 at 12 hours. Proposed approval ceiling $6 PRE-TAX, subject to actual account quote, monthly billing/proration, egress and teardown mechanics. This is not a spending authorization or guaranteed final invoice. No paid NAT gateway, snapshots, managed services, disk sharing, reservations or ongoing retained disks in this estimate. Delete VM, disks and public IP at the stop, after preserving small reports. Taxes/currency conversion and non-free egress must be checked before commitment; if total exceeds approved ceiling, stop before provisioning. Full data staging would require at least roughly 600 GiB, or a separately scoped sequential-stream/delete workflow. A full run is not approved by pilot approval.

Current local workspace: 2 CPUs, 1.9 GiB RAM, no swap, 8.2 GiB free disk. It cannot host this pinned profiler/database. No provider account or provisioning capability is established by this research.

## Sources
- https://visualization.osdr.nasa.gov/biodata/api/v2/dataset/OSD-742/files/
- https://osdr.nasa.gov/bio/repo/data/studies/OSD-742
- https://github.com/biobakery/MetaPhlAn/wiki/MetaPhlAn-4
- https://github.com/biobakery/MetaPhlAn/releases
- https://cmprod1.cibio.unitn.it/biobakery4/metaphlan_databases/
- https://cmprod1.cibio.unitn.it/biobakery4/metaphlan_databases/bowtie2_indexes/
- https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/general-purpose/dsv5-series
- https://learn.microsoft.com/en-us/azure/virtual-machines/disks-types
- https://azure.microsoft.com/en-us/pricing/details/managed-disks/
- https://prices.azure.com/api/retail/prices

Exact filtered retail API request URLs/results, per-file byte inventory and pilot manifest are stored alongside this proposal. Counts are file-metadata and QC measurements, not independently analyzed biology.
