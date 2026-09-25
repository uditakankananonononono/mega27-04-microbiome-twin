#!/bin/bash
# Chain C: waits for TS stream B, then 2b on Ocean + Soil_Vivo, then T1 shard 0, then T2
cd ~/mega27/item04/mega27-04-microbiome-twin
while ! grep -q STREAM_B_DONE /tmp/bench_ts_b.log 2>/dev/null; do sleep 60; done
python3 run_bench.py Ocean graphtwin2b 10 >> /tmp/bench_2b_c.log 2>&1
python3 run_bench.py Soil_Vivo graphtwin2b 10 >> /tmp/bench_2b_c.log 2>&1
echo B2C_DONE >> /tmp/bench_2b_c.log
OMP_NUM_THREADS=1 T1_SHARD=0 T1_NSHARD=2 python3 scripts/twindiscovery_t1.py >> /tmp/t1_s0.log 2>&1
echo T1_S0_DONE >> /tmp/t1_s0.log
while [ ! -f results/twindiscovery_t1_shard1.done ]; do sleep 120; done
python3 scripts/twindiscovery_t1.py >> /tmp/t1_consensus.log 2>&1
python3 scripts/twindiscovery_t2.py >> /tmp/t2.log 2>&1
echo CHAIN_C_ALL_DONE >> /tmp/t2.log
