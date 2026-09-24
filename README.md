# mega27-04-microbiome-twin
Microbiome digital twin: predict community composition from species assemblage, benchmarked on the six real ecosystem datasets of the cNODE study (Michel-Mata et al. 2022, PMC9221840; data via github.com/yixueyang/cNODE).
Models on identical folds: presence-mean null, cNODE re-implementation, gLV replicator, GraphTwin (attention GNN over present taxa with learned interaction gates).
Run tests: `python -m pytest -q`. Run benchmark: `python run_bench.py Drosophila_Gut presence_mean,cnode,glv,graphtwin 10`.
